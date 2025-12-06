"""PRM IMEI Importer - reads Excel file and populates database"""
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from models import Retailer, Product, PrmInventorySnapshot, Activation


def categorize_product(name: str) -> str:
    """
    Categorize product based on name
    
    Returns: 'TV', 'Pad', 'Phones', or 'eco'
    """
    if not name:
        return 'eco'
    
    name_lower = name.lower()
    
    if 'tv' in name_lower:
        return 'TV'
    
    if 'pad' in name_lower or 'tablet' in name_lower or ' tab ' in name_lower:
        return 'Pad'
    
    phone_keywords = ['redmi', 'xiaomi', ' mi ', 'poco', 'note', ' 5g', ' 4g', 'phone', 'mobile']
    if any(keyword in name_lower for keyword in phone_keywords):
        return 'Phones'
    
    return 'eco'


def import_prm_imei_file(path: str, db_session: Session) -> dict:
    """
    Import PRM IMEI Excel file into database
    
    Args:
        path: Path to Excel file
        db_session: SQLAlchemy database session
        
    Returns:
        dict: Import statistics
        
    Raises:
        Exception: If file read fails or data is invalid
    """
    print(f"\nReading Excel file: {path}")
    
    try:
        df = pd.read_excel(path, engine='openpyxl')
    except FileNotFoundError:
        raise Exception(f"File not found: {path}")
    except Exception as e:
        raise Exception(f"Failed to read Excel file: {str(e)}")
    
    print(f"Found {len(df)} rows in Excel file")
    print(f"Columns: {list(df.columns)}")
    
    # FIXED: Define column indices based on actual Excel structure
    # These indices are 0-based and match the typical PRM IMEI export format
    COL_IMEI1 = 0           # IMEI1
    COL_GOODS_ID = 2        # Goods ID
    COL_PRODUCT_NAME = 3    # Product Name
    COL_STATUS = 4          # Status
    COL_ACTIVATION_TIME = 5 # Activation Time
    COL_RETAILER_ID = 18    # Retailer ID
    COL_RETAILER_NAME = 19  # Retailer Name
    
    # Validate that we have enough columns
    if len(df.columns) < 20:
        print(f"⚠ Warning: Expected at least 20 columns, found {len(df.columns)}")
        print("Attempting import anyway, but results may be incorrect...")
    
    retailers_upserted = 0
    products_upserted = 0
    inventory_dict = {}
    activations_list = []
    
    print("\nProcessing rows...")
    processed_count = 0
    error_count = 0
    
    for idx, row in df.iterrows():
        try:
            # Extract and clean data
            retailer_code = str(row.iloc[COL_RETAILER_ID]).strip() if pd.notna(row.iloc[COL_RETAILER_ID]) else None
            retailer_name = str(row.iloc[COL_RETAILER_NAME]).strip() if pd.notna(row.iloc[COL_RETAILER_NAME]) else None
            goods_id = str(row.iloc[COL_GOODS_ID]).strip() if pd.notna(row.iloc[COL_GOODS_ID]) else None
            product_name = str(row.iloc[COL_PRODUCT_NAME]).strip() if pd.notna(row.iloc[COL_PRODUCT_NAME]) else None
            status = str(row.iloc[COL_STATUS]).strip().lower() if pd.notna(row.iloc[COL_STATUS]) else ""
            activation_time = row.iloc[COL_ACTIVATION_TIME] if pd.notna(row.iloc[COL_ACTIVATION_TIME]) else None
            imei1 = str(row.iloc[COL_IMEI1]).strip() if pd.notna(row.iloc[COL_IMEI1]) else None
            
            # Skip rows without goods_id
            if not goods_id or goods_id == 'nan':
                continue
            
            # Handle retailer
            retailer_obj = None
            if retailer_code and retailer_name and retailer_code != 'nan':
                retailer_obj = db_session.query(Retailer).filter_by(retailer_code=retailer_code).first()
                
                if retailer_obj:
                    # Update name if changed
                    if retailer_obj.name != retailer_name:
                        retailer_obj.name = retailer_name
                else:
                    # Create new retailer
                    retailer_obj = Retailer(retailer_code=retailer_code, name=retailer_name)
                    db_session.add(retailer_obj)
                    db_session.flush()
                    retailers_upserted += 1
            
            # Handle product
            category = categorize_product(product_name)
            product_obj = db_session.query(Product).filter_by(goods_id=goods_id).first()
            
            if product_obj:
                # Update existing product
                if product_name and product_obj.name != product_name:
                    product_obj.name = product_name
                if product_obj.category != category:
                    product_obj.category = category
            else:
                # Create new product
                product_obj = Product(
                    goods_id=goods_id,
                    name=product_name,
                    category=category
                )
                db_session.add(product_obj)
                db_session.flush()
                products_upserted += 1
            
            # Handle inventory (only for "inward by retailer" status)
            if retailer_obj and "inward by retailer" in status:
                key = (retailer_obj.id, goods_id)
                inventory_dict[key] = inventory_dict.get(key, 0) + 1
            
            # Handle activations
            if activation_time and imei1 and imei1 != 'nan':
                # Convert activation time to datetime if string
                if isinstance(activation_time, str):
                    try:
                        activation_time = pd.to_datetime(activation_time)
                    except:
                        activation_time = None
                
                if activation_time:
                    activations_list.append({
                        'goods_id': goods_id,
                        'imei_sn': imei1,
                        'retailer_id': retailer_obj.id if retailer_obj else None,
                        'activation_status': 'Activated',
                        'activation_time': activation_time
                    })
            
            processed_count += 1
            
            # Progress indicator
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(df)} rows...")
                
        except Exception as e:
            error_count += 1
            print(f"Warning: Error processing row {idx}: {str(e)}")
            continue
    
    # Commit retailer and product changes
    db_session.commit()
    print(f"\n✓ Processed {processed_count} rows ({error_count} errors)")
    print(f"✓ Upserted {retailers_upserted} retailers")
    print(f"✓ Upserted {products_upserted} products")
    
    # Rebuild inventory snapshot (replace all existing data)
    print("\n⟳ Rebuilding inventory snapshot...")
    db_session.query(PrmInventorySnapshot).delete()
    
    for (retailer_id, goods_id), quantity in inventory_dict.items():
        snapshot = PrmInventorySnapshot(
            retailer_id=retailer_id,
            goods_id=goods_id,
            quantity=quantity,
            last_seen=datetime.now()
        )
        db_session.add(snapshot)
    
    db_session.commit()
    print(f"✓ Created {len(inventory_dict)} inventory snapshot records")
    
    # Clear and insert activations
    print("\n⟳ Inserting activations...")
    db_session.query(Activation).delete()
    
    for activation_data in activations_list:
        activation = Activation(**activation_data)
        db_session.add(activation)
    
    db_session.commit()
    print(f"✓ Inserted {len(activations_list)} activation records")
    
    print("\n" + "=" * 60)
    print("Import completed successfully!")
    print("=" * 60)
    
    return {
        "retailers_upserted": retailers_upserted,
        "products_upserted": products_upserted,
        "inventory_rows": len(inventory_dict),
        "activations_rows": len(activations_list)
    }
