import os
import json
import django
from decimal import Decimal
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmbh_system.settings')
django.setup()

from django.core.files import File
from core.models import Product, ProductImage


def load_catalog():
    """Load the apparel catalog JSON file"""
    catalog_path = os.path.join(os.path.dirname(__file__), 'apparel_catalog.json')
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_folder_from_filepath(filepath):
    """Extract the folder name from the new_filepath field"""
    # e.g., "classified\\Mens_Jacket\\MJKT-001_Jacket_Mens_Puffer_Jacket.jpeg"
    # -> "Mens_Jacket"
    parts = filepath.replace('/', '\\').split('\\')
    if len(parts) >= 2:
        return parts[1]  # The folder name after 'classified'
    return None


def group_items_by_folder(catalog_items):
    """
    Group catalog items by their folder name (style category).
    All items in the same folder are different color variants of the same style.
    """
    folder_groups = defaultdict(list)
    for item in catalog_items:
        filepath = item.get('new_filepath', '')
        folder = get_folder_from_filepath(filepath)
        if folder:
            folder_groups[folder].append(item)
    return folder_groups


def folder_to_style_name(folder_name):
    """Convert folder name to a readable style name"""
    # e.g., "Mens_Jacket" -> "Men's Jacket"
    # e.g., "Ladies_Sweatshirt" -> "Ladies Sweatshirt"
    name = folder_name.replace('_', ' ')
    name = name.replace('Mens ', "Men's ")
    name = name.replace('Womens ', "Women's ")
    name = name.replace('Kids ', "Kids' ")
    return name


def extract_category_from_folder(folder_name):
    """Extract category from folder name"""
    # e.g., "Mens_Jacket" -> "Jacket"
    # e.g., "Ladies_Sweatshirt" -> "Sweatshirt"
    parts = folder_name.split('_')
    if len(parts) >= 2:
        # Join all parts after the audience prefix (Mens, Ladies, Kids, Unisex)
        category = ' '.join(parts[1:])
        return category
    return folder_name


def extract_audience_from_folder(folder_name):
    """Extract target audience from folder name"""
    # e.g., "Mens_Jacket" -> "Mens"
    parts = folder_name.split('_')
    if parts:
        return parts[0]
    return "Unisex"


def create_products():
    """Create products from the apparel catalog, grouped by folder (style category)"""
    
    # Clear existing products and images
    ProductImage.objects.all().delete()
    Product.objects.all().delete()
    print("Cleared existing products and images.\n")
    
    # Load catalog
    catalog_items = load_catalog()
    print(f"Loaded {len(catalog_items)} items from apparel catalog.\n")
    
    # Group items by folder (each folder = one style with multiple color variants)
    folder_groups = group_items_by_folder(catalog_items)
    print(f"Found {len(folder_groups)} style folders.\n")
    
    base_path = os.path.dirname(__file__)
    products_created = 0
    images_added = 0
    
    for folder_name, items in folder_groups.items():
        # Use folder name as the style name
        style_name = folder_to_style_name(folder_name)
        
        # Get category from folder name
        category = extract_category_from_folder(folder_name)
        
        # Get audience prefix for code
        audience = extract_audience_from_folder(folder_name)
        audience_prefix = {
            'Mens': 'M',
            'Ladies': 'L',
            'Kids': 'K',
            'Unisex': 'U'
        }.get(audience, 'X')
        
        # Generate a unique product code based on folder
        # Use audience prefix + category abbreviation
        cat_abbrev = ''.join(word[0:3].upper() for word in category.split())[:6]
        product_code = f"{audience_prefix}-{cat_abbrev}-{len(items):02d}"
        
        # Use the first item for product details (they should be similar)
        first_item = items[0]
        
        # Collect all colors from items in this folder
        all_colors = set()
        for item in items:
            colors = item.get('primary_colors', [])
            all_colors.update(colors)
        available_colors = ', '.join(sorted(all_colors)) if all_colors else first_item.get('available_colors', 'Multiple colors')
        
        # Create description mentioning the variety
        description = f"{style_name} collection with {len(items)} color variants available. {first_item.get('description', '')}"
        
        try:
            product = Product.objects.create(
                code=product_code,
                style_name=style_name,
                category=category if category in dict(Product.CATEGORY_CHOICES) else 'Other',
                fabric_type=first_item.get('fabric_type', 'Mixed'),
                gsm=first_item.get('gsm', 'Medium'),
                available_colors=available_colors,
                size_range=first_item.get('size_range', 'S - XL'),
                moq=first_item.get('moq', 500),
                target_price=Decimal(str(first_item.get('target_price', 10.0))),
                description=description,
            )
            products_created += 1
            print(f"[+] Created: {style_name} ({product_code}) - {len(items)} color variants")
            
            # Add all images from this folder (each image = different color variant)
            is_first_image = True
            for item in items:
                image_path = item.get('new_filepath', '')
                if image_path:
                    # Convert relative path to absolute path
                    full_image_path = os.path.join(base_path, image_path)
                    
                    if os.path.exists(full_image_path):
                        try:
                            with open(full_image_path, 'rb') as img_file:
                                # Extract just the filename for storage
                                image_filename = os.path.basename(image_path)
                                
                                product_image = ProductImage(
                                    product=product,
                                    is_main=is_first_image  # First image is main
                                )
                                product_image.image.save(image_filename, File(img_file), save=True)
                                images_added += 1
                                is_first_image = False
                        except Exception as e:
                            print(f"    [!] Error adding image {image_path}: {e}")
                    else:
                        print(f"    [!] Image not found: {full_image_path}")
        
        except Exception as e:
            print(f"[-] Error creating {style_name}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Products created: {products_created}")
    print(f"  Images added: {images_added}")
    print(f"  Total products in DB: {Product.objects.count()}")
    print(f"  Total images in DB: {ProductImage.objects.count()}")
    print(f"{'='*60}")


def list_folders():
    """List all folders in classified directory and their image counts"""
    classified_path = os.path.join(os.path.dirname(__file__), 'classified')
    print("Folders in classified directory:\n")
    for folder in sorted(os.listdir(classified_path)):
        folder_path = os.path.join(classified_path, folder)
        if os.path.isdir(folder_path):
            image_count = len([f for f in os.listdir(folder_path) if f.endswith(('.jpeg', '.jpg', '.png'))])
            print(f"  {folder}: {image_count} images")


def list_categories():
    """List all unique categories in the catalog"""
    catalog_items = load_catalog()
    categories = set(item['category'] for item in catalog_items)
    print("Categories in catalog:")
    for cat in sorted(categories):
        count = sum(1 for item in catalog_items if item['category'] == cat)
        print(f"  - {cat}: {count} items")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--categories':
            list_categories()
        elif sys.argv[1] == '--folders':
            list_folders()
    else:
        create_products()
