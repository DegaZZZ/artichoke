from PIL import Image
from io import BytesIO
import requests

def create_open_graph_image(image_urls, output_path):
    # Function to fetch and resize an image from a URL
    def fetch_and_resize_image(url, size):
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return image.resize(size)
        else:
            print(f"Failed to retrieve the image from {url}")
            return None

    images = [fetch_and_resize_image(url, (243, 412)) for url in image_urls]

    # Calculate the base image dimensions for a 16:9 aspect ratio
    image_count = len(images)
    spacing = 50  # Space between images
    total_image_width = (243, 412)[0] * image_count
    total_spacing_width = spacing * (image_count - 1)
    content_width = total_image_width + total_spacing_width

    aspect_ratio = 16 / 9
    base_height = int(content_width / aspect_ratio)
    base_height += 100  # Add padding to the height
    base_width = int(base_height * aspect_ratio)

    # Create a black rectangle as the base image
    base_image = Image.new('RGB', (base_width, base_height), 'black')

    # Calculate positions to evenly space and center the images
    start_x = (base_width - content_width) // 2
    positions = []
    current_x = start_x
    for _ in range(image_count):
        positions.append((current_x, (base_height - (243, 412)[1]) // 2))
        current_x += (243, 412)[0] + spacing

    # Paste the images onto the base image
    for img, pos in zip(images, positions):
        if img is not None:
            base_image.paste(img, pos)

    # Save the final image
    base_image.save(output_path)