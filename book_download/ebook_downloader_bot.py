import logging
import os
import re

from telegram.ext import Updater
from telegram.ext import CommandHandler
import cpsdownloader

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start(bot, update, args):
    asin = args[0]
    chat_id = update.message.chat_id
    if len(asin) != 10:
        bot.send_message(chat_id=chat_id, text="Please provide proper 10 digit ASIN")
        return
    pattern = re.compile('^B[a-zA-Z0-9]+$')
    gr = pattern.match(asin)
    if gr is None:
        bot.send_message(chat_id=chat_id, text="Please provide proper 10 digit ASIN")
        return
    bot.send_message(chat_id=chat_id, text="Initiating download. Please relax for some time")
    status = cpsdownloader.download_book(asin)
    logger.info(' Status of book downloader: {}---'.format(status))
    logger.info('Does book Local Path {}: '.format(str(os.path.exists(status))))
    if 'Error:' in status or not os.path.exists(status):
        logger.info('Sending err msg back to user')
        bot.send_message(chat_id=chat_id, text='Sorry!!! Could not process download and the error is {}'.format(status),
                         timeout=1500)
    else:
        logger.info('Replying back to user')
        update.message.reply_text("Book Found!!! Please wait for some more time while your book is on the way",
                                  timeout=1500)
        status = cpsdownloader.get_book_from_local(asin, status)
        if 'Error:' in status or not os.path.exists(status):
            bot.send_message(chat_id=chat_id,
                             text='Sorry!!! Could not process download and the error is {}'.format(status))
            return
        try:
            msg = bot.sendDocument(chat_id=chat_id, document=open(status.strip(), 'rb'), timeout=30000)
            logger.info("Msg FileID: " + msg.document.file_id)
        except Exception as e:
            logger.critical('cannot send document {}'.format(status.strip()))
            logger.critical(e.message)
        else:
            logger.info('successfully sent document {}'.format(status.strip()))
        finally:
            os.remove(status.strip())


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(token='637573336:AAEYi2dkCuAlWqdt9zNXGit6iDIFTO3JfGY')
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('asin', start, pass_args=True)
    dispatcher.add_handler(start_handler)
    # log all errors
    dispatcher.add_error_handler(error)
    # Start the Bot
    updater.start_polling()


if __name__ == '__main__':
    main()
