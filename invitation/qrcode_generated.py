# import qrcode
# from PIL import Image

# def generate_fancy_qr(data, logo_path, output_path, qr_color="black", bg_color="white", box_size=10, border=4):
#     # Create QR code instance
#     qr = qrcode.QRCode(
#         version=1,  # Controls the size of the QR Code (1 is 21x21 matrix)
#         error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
#         box_size=box_size,  # Size of each box in pixels
#         border=border,  # Border size in boxes
#     )

#     # Add data to the QR code
#     qr.add_data(data)
#     qr.make(fit=True)

#     # Create an image from the QR Code instance
#     qr_img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert('RGBA')

#     # Open the logo image
#     logo = Image.open(logo_path)

#     # Calculate the size of the logo
#     logo_size = qr_img.size[0] // 4  # Logo size is 1/4th of the QR code size
#     logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)  # Use LANCZOS for high-quality resizing

#     # Calculate the position to paste the logo
#     logo_pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)

#     # Paste the logo onto the QR code
#     qr_img.paste(logo, logo_pos, logo)

#     # Save the final QR code
#     qr_img.save(output_path)

#     print(f"Fancy QR code saved to {output_path}")

# # Example usage
# data = "https://eventic.in/"
# logo_path = "Eventic-Logo.png"  # Path to your logo image
# output_path = "fancy_qr_code.png"

# generate_fancy_qr(data, logo_path, output_path, qr_color="#000", bg_color="#fff", box_size=20, border=4)


from PIL import Image, ImageDraw, ImageFont

# Function to create the invitation
def create_invitation(groom_name, bride_name, event_date, invitation_text, qr_code_path, output_path):
    # Create a blank image with a white background
    width, height = 800, 1200  # Size of the invitation
    invitation = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(invitation)

    # Load a fancy font (you can change the font path to your preferred font)
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 40)  # Bold font for titles
        font_text = ImageFont.truetype("arial.ttf", 30)     # Regular font for text
    except IOError:
        print("Font not found. Using default font.")
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Add the title
    title = "Wedding Invitation"
    # Use textbbox to get the bounding box of the text
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]  # Calculate width
    title_height = title_bbox[3] - title_bbox[1]  # Calculate height
    draw.text(((width - title_width) // 2, 50), title, fill="black", font=font_title)

    # Add groom and bride names
    names = f"{groom_name} & {bride_name}"
    names_bbox = draw.textbbox((0, 0), names, font=font_title)
    names_width = names_bbox[2] - names_bbox[0]
    names_height = names_bbox[3] - names_bbox[1]
    draw.text(((width - names_width) // 2, 150), names, fill="gold", font=font_title)

    # Add event date
    date_text = f"Date: {event_date}"
    date_bbox = draw.textbbox((0, 0), date_text, font=font_text)
    date_width = date_bbox[2] - date_bbox[0]
    date_height = date_bbox[3] - date_bbox[1]
    draw.text(((width - date_width) // 2, 250), date_text, fill="black", font=font_text)

    # Add invitation text
    text_y = 350
    for line in invitation_text.split("\n"):
        line_bbox = draw.textbbox((0, 0), line, font=font_text)
        line_width = line_bbox[2] - line_bbox[0]
        line_height = line_bbox[3] - line_bbox[1]
        draw.text(((width - line_width) // 2, text_y), line, fill="black", font=font_text)
        text_y += line_height + 10  # Add spacing between lines

    # Add the QR code at the bottom
    qr_code = Image.open(qr_code_path)
    qr_code = qr_code.resize((200, 200))  # Resize QR code to fit
    qr_position = ((width - qr_code.width) // 2, height - qr_code.height - 50)
    invitation.paste(qr_code, qr_position)

    # Save the invitation
    invitation.save(output_path)
    print(f"Invitation saved to {output_path}")

# Example data
groom_name = "John Doe"
bride_name = "Jane Smith"
event_date = "November 15, 2023"
invitation_text = "We cordially invite you to celebrate our special day.\nJoin us for a joyous occasion filled with love and happiness."
qr_code_path = "Eventic-Logo.png"  # Path to the QR code with brand logo
output_path = "wedding_invitation_with_brand_logo.png"

# Create the invitation
create_invitation(groom_name, bride_name, event_date, invitation_text, qr_code_path, output_path)