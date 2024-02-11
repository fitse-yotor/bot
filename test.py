import datetime

from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext


# Telegram Bot token, replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual token
TOKEN = '6926859115:AAEf_kzECrM45BoTNeabEF2DYsg5EoXS-ZU'

# Conversation states
AMOUNT, SENDER_NAME, RECEIVER_NAME, ACCOUNT_NO, REASON = range(5)
DEFAULT_TEMPLATE_IMAGE_PATH = "New1.jpeg"
DEFAULT_SENDER_NAME = "Abdisa Gemeda Chalutu"


def generate_receipt(amount, sender_name, receiver_name, account_no, reason, template_image_path=DEFAULT_TEMPLATE_IMAGE_PATH):
    current_date = datetime.datetime.now().strftime("%d-%b-%Y")

  
    
    # Format amount as currency (with comma separators and two decimal places)
    formatted_amount = "{:,.2f}".format(float(amount))

    # Capitalize sender and receiver names
    sender_name = sender_name.upper()
    receiver_name = receiver_name.upper()

# Split sender name into multiple lines if it's too long
    sender_lines = [sender_name[i:i+30] for i in range(0, len(sender_name), 30)]
    sender_text = "\n".join(sender_lines)

    # Split receiver name into multiple lines if it's too long
    receiver_lines = [receiver_name[i:i+30] for i in range(0, len(receiver_name), 30)]
    receiver_text = "\n".join(receiver_lines)

    receipt_text = f"ETB {formatted_amount} debited from {sender_text} \nfor {receiver_text} -ETB-{account_no} \n({reason} done via Mobile) {current_date} \nwith transaction ID: FT24041YX1JB."
    # Open the template image
    template_image = Image.open(template_image_path)

    # Initialize drawing context
    draw = ImageDraw.Draw(template_image)

    # Set font and size
    font_size = 60
    font = ImageFont.truetype("calibrib.ttf", font_size)

    # Calculate text width and height
    text_width = max([draw.textsize(line, font=font)[0] for line in receipt_text.split("\n")])
    text_height = sum([draw.textsize(line, font=font)[1] for line in receipt_text.split("\n")])

    # Calculate starting position for text
    x = 100  # Padding from left
    y = 550  # Padding from top

    # Draw text on the image border with dark gray color
    for line in receipt_text.split("\n"):
        draw.text((x, y), line, fill="#111111", font=font)
        y += font_size + 5  # Move to next line

    # Save the modified image
    output_image_path = "receipt_with_text.jpg"
    template_image.save(output_image_path)

    return output_image_path




def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Welcome to the Receipt Generator Bot! Please provide the following details:\n\n'
                              'Amount:')
    return AMOUNT

def receive_amount(update: Update, context: CallbackContext) -> int:
    context.user_data["amount"] = update.message.text
    update.message.reply_text('Sender Name (leave empty to use default):')
    return SENDER_NAME

def receive_sender_name(update: Update, context: CallbackContext) -> int:
    if update.message.text:
        sender_name = update.message.text.title()  # Capitalize sender name
    else:
        sender_name = DEFAULT_SENDER_NAME
    
    context.user_data["sender_name"] = sender_name
    update.message.reply_text('Receiver Name:')
    return RECEIVER_NAME

def receive_receiver_name(update: Update, context: CallbackContext) -> int:
    receiver_name = update.message.text.title()  # Capitalize receiver name
    context.user_data["receiver_name"] = receiver_name
    update.message.reply_text('Account No:')
    return ACCOUNT_NO

def receive_account_no(update: Update, context: CallbackContext) -> int:
    context.user_data["account_no"] = update.message.text
    update.message.reply_text('Reason:')
    return REASON

def receive_reason(update: Update, context: CallbackContext) -> int:
    context.user_data["reason"] = update.message.text

    # Generate receipt
    receipt_image_path = generate_receipt(context.user_data["amount"], context.user_data["sender_name"],
                                           context.user_data["receiver_name"], context.user_data["account_no"],
                                           context.user_data["reason"])

    # Send the receipt image
    update.message.reply_photo(open(receipt_image_path, 'rb'))

    # Clear user data
    context.user_data.clear()

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Receipt generation canceled. Send /start to generate a new receipt.')
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AMOUNT: [MessageHandler(Filters.text & ~Filters.command, receive_amount)],
            SENDER_NAME: [MessageHandler(Filters.text & ~Filters.command, receive_sender_name)],
            RECEIVER_NAME: [MessageHandler(Filters.text & ~Filters.command, receive_receiver_name)],
            ACCOUNT_NO: [MessageHandler(Filters.text & ~Filters.command, receive_account_no)],
            REASON: [MessageHandler(Filters.text & ~Filters.command, receive_reason)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
