import cv2
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend - saves files without displaying
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# Folders
input_folder = 'inputs'
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

# Find all images in the inputs folder
image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
image_files = []
for ext in image_extensions:
    image_files.extend(glob.glob(os.path.join(input_folder, ext)))
    image_files.extend(glob.glob(os.path.join(input_folder, ext.upper())))

if not image_files:
    print(f"No images found in '{input_folder}/' folder.")
    print("Please add images (.jpg, .png, .bmp, .tiff) to the inputs folder.")
    exit(1)

print(f"Found {len(image_files)} image(s) in '{input_folder}/'")


def create_color_histogram(img_rgb, ax, title):
    """Create a histogram where each bar is colored by the average color at that brightness level."""
    # Calculate brightness (luminance) for each pixel
    brightness = np.mean(img_rgb, axis=2).astype(int)
    
    # For each brightness level, find the average color of pixels at that level
    colors = []
    counts = []
    
    for level in range(256):
        mask = brightness == level
        count = np.sum(mask)
        counts.append(count)
        
        if count > 0:
            # Average color of all pixels at this brightness level
            avg_color = img_rgb[mask].mean(axis=0) / 255.0  # Normalize to 0-1 for matplotlib
            colors.append(avg_color)
        else:
            colors.append([0, 0, 0])  # Black for empty bins
    
    # Plot each bar with its corresponding color
    for level in range(256):
        if counts[level] > 0:
            ax.bar(level, counts[level], width=1, color=colors[level], edgecolor='none')
    
    ax.set_title(title)
    ax.set_xlabel('Pixel Intensity (0=dark, 255=bright)')
    ax.set_ylabel('Pixel Count')
    ax.set_xlim([0, 256])


def process_image(image_path):
    """Process a single image and generate all histogram outputs."""
    # Get the base name without extension for output filenames
    basename = os.path.splitext(os.path.basename(image_path))[0]
    
    print(f"\nProcessing: {image_path}")
    
    # Load the image
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print(f"  Error: Could not load image '{image_path}'")
        return
    
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # --- Figure 1: Original Image with Color Histogram ---
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.imshow(img_rgb)
    ax1.set_title('Original Image')
    ax1.axis('off')
    create_color_histogram(img_rgb, ax2, 'Color Histogram (bars colored by avg color at each brightness)')
    plt.tight_layout()
    fig1.savefig(os.path.join(output_folder, f'{basename}_histogram_original_color.png'), dpi=150)
    plt.close()

    # --- Figure 2: RGB Histograms ---
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.imshow(img_rgb)
    ax1.set_title('Original Image')
    ax1.axis('off')
    colors_rgb = ['red', 'green', 'blue']
    for i, color in enumerate(colors_rgb):
        ax2.hist(img_rgb[:,:,i].ravel(), 256, range=[0, 256], color=color, alpha=0.5, label=color.capitalize())
    ax2.set_title('RGB Channel Histograms')
    ax2.set_xlabel('Pixel Intensity (0=black, 255=white)')
    ax2.set_ylabel('Pixel Count')
    ax2.legend()
    plt.tight_layout()
    fig2.savefig(os.path.join(output_folder, f'{basename}_histogram_rgb.png'), dpi=150)
    plt.close()

    # --- Figure 3: Low-Res Image with Color Histogram (showing bunching) ---
    # Scale down dramatically to show histogram bunching effect
    # Using only 2% of original size (e.g., a 1000px image becomes 20px)
    scale_factor = 0.02
    width = int(img_rgb.shape[1] * scale_factor)
    height = int(img_rgb.shape[0] * scale_factor)
    # Ensure minimum size of 1x1
    width = max(1, width)
    height = max(1, height)
    # Use INTER_NEAREST to avoid interpolation smoothing, which emphasizes bunching
    img_low_res = cv2.resize(img_rgb, (width, height), interpolation=cv2.INTER_NEAREST)

    # Save the low-res image
    lowres_path = os.path.join(output_folder, f'{basename}_lowres.jpg')
    cv2.imwrite(lowres_path, cv2.cvtColor(img_low_res, cv2.COLOR_RGB2BGR))
    print(f"  Low-res image saved: {width}x{height} pixels")

    fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.imshow(img_low_res)
    ax1.set_title(f'Low-Res Image ({width}x{height})')
    ax1.axis('off')
    create_color_histogram(img_low_res, ax2, 'Color Histogram - Low Res (shows bunching)')
    plt.tight_layout()
    fig3.savefig(os.path.join(output_folder, f'{basename}_histogram_lowres_color.png'), dpi=150)
    plt.close()

    # --- Figure 4: Low-Res Image with RGB Channel Histograms ---
    fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.imshow(img_low_res)
    ax1.set_title(f'Low-Res Image ({width}x{height})')
    ax1.axis('off')
    for i, color in enumerate(colors_rgb):
        ax2.hist(img_low_res[:,:,i].ravel(), 256, range=[0, 256], color=color, alpha=0.5, label=color.capitalize())
    ax2.set_title('RGB Channel Histograms - Low Res (shows bunching)')
    ax2.set_xlabel('Pixel Intensity (0=black, 255=white)')
    ax2.set_ylabel('Pixel Count')
    ax2.legend()
    plt.tight_layout()
    fig4.savefig(os.path.join(output_folder, f'{basename}_histogram_lowres_rgb.png'), dpi=150)
    plt.close()

    # --- Figure 5: Grayscale Image and Histogram ---
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.imshow(img_gray, cmap='gray')
    ax1.set_title('Grayscale Image')
    ax1.axis('off')
    ax2.hist(img_gray.ravel(), 256, range=[0, 256], color='gray')
    ax2.set_title('Grayscale Histogram')
    ax2.set_xlabel('Pixel Intensity (0=black, 255=white)')
    ax2.set_ylabel('Pixel Count')
    plt.tight_layout()
    fig5.savefig(os.path.join(output_folder, f'{basename}_histogram_grayscale.png'), dpi=150)
    plt.close()

    print(f"  Generated 5 histogram images for '{basename}'")


# Process all images
for image_path in image_files:
    process_image(image_path)

print(f"\n{'='*50}")
print(f"All outputs saved to '{output_folder}/' folder")
print(f"For each image, the following files were created:")
print("  - <name>_histogram_original_color.png")
print("  - <name>_histogram_rgb.png")
print("  - <name>_histogram_lowres_color.png")
print("  - <name>_histogram_lowres_rgb.png")
print("  - <name>_histogram_grayscale.png")
print("  - <name>_lowres.jpg")