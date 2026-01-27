# DMBH - Apparel Buying House Management System

A comprehensive web-based management system for **DM Design**, an apparel buying house. This updated platform facilitates product showcasing, buyer interaction, order management (`Cart` & `Order` systems), and sample requests.

## 🚀 Key Features

### 🛍️ User & Buyer Experience
- **Product Catalog**: Browse a wide range of apparel (Men's, Women's, Kids) with filtering by category.
- **Detailed Product Views**: High-quality image galleries, specifications (GSM, Fabric, MOQ), and related item suggestions.
- **Shopping Cart**:
  - Add items to cart with specific quantities.
  - Review cart, update quantities, or remove items.
  - **Multi-Item Checkout**: Place a single order containing multiple different products.
- **User Dashboard**:
  - Track **Active Orders** (with full item breakdown).
  - Monitor **Sample Requests** status.
  - View **Inquiry** history and Admin replies.
  - **Profile Management**: View account details (Phone, Email, Role).

### 🛠️ Administration & Management
- **Order Management**:
  - View orders with unique Order Numbers (e.g., `ORD-8X92...`).
  - Update status (`Converted`, `In Progress`, `Shipped`, etc.).
  - See total items and total value per order.
- **Content Management**:
  - Manage Products, Categories, and Images via Django Admin.
  - Update Inquiry and Sample Request statuses.

### 🎨 Design & UI
- **Modern Aesthetic**: Clean, minimalist design with a subtle apparel-themed background texture.
- **Responsive Layout**: Widened 1600px container for better visibility on large screens.
- **Interactive Elements**:
  - Hover effects on product cards.
  - Confirmation modals for checkout.
  - Dynamic status badges in dashboard.

## 📦 Installation & Setup

### 1. Prerequisites
- Python 3.10+
- `pip` (Python Package Manager)

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install django pillow
```

### 4. Database Setup
```bash
# Apply migrations to create database schema
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate Initial Data
The system comes with a script to populate the database from the `apparel_catalog.json` file.
```bash
python populate_data.py
```
*Note: This script initializes the Product and ProductImage tables based on the classified folder structure.*

### 6. Create Admin User
```bash
python manage.py createsuperuser
# Or use the helper script if available:
# python create_superuser.py
```

### 7. Run the Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

## 📂 Project Structure

- **core/**: Main Django app containing Models, Views, Forms, and Admin config.
  - `models.py`: Defines `Product`, `Order`, `OrderItem`, `Cart`, `User`, etc.
  - `views.py`: Logic for checkout, dashboard, and product browsing.
- **templates/**: HTML templates using Bootstrap 5.
  - `core/`: Dashboard, Checkout, Cart, and Product templates.
  - `base.html`: Main layout with Navigation and Footer.
- **static/**: CSS, JavaScript, and static images.
- **media/**: User-uploaded content (Product images).

## 🛒 Order Flow
1.  **User Login**: Buyers must log in to place orders.
2.  **Add to Cart**: Users select `Quantity` on a product page and click "Add to Order".
3.  **Review**: The "Shopping Cart" page allows modifying the request.
4.  **Checkout**: Users confirm the total amount and place the order via a Confirmation Modal.
5.  **Tracking**: The Order is saved to the database and appears in the User Dashboard and Admin Panel.

---
**Developed for DM Design**
