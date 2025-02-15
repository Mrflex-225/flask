# app/routes/products.py
from flask import Blueprint, request, jsonify, current_app
import datetime, traceback
from app import db
from app.models import Product, Possede

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['POST'])
def add_products():
    try:
        data_list = request.get_json()
        if not isinstance(data_list, list):
            return jsonify({"error": "Le format attendu est une liste d'objets"}), 400

        result = []
        for data in data_list:
            if 'name' not in data or 'qr_code' not in data or 'id_utilisateur' not in data:
                return jsonify({"error": "Le nom, le QR code et l'id utilisateur sont obligatoires"}), 400

            existing_product = Product.query.filter_by(qr_code=data['qr_code']).first()
            if existing_product:
                product_id = existing_product.idProduit
                product_info = existing_product
            else:
                new_product = Product(
                    name=data['name'],
                    categorie=data.get('categorie'),
                    qr_code=data['qr_code'],
                    poids=data.get('poids'),
                    volume=data.get('volume'),
                )
                db.session.add(new_product)
                db.session.commit()
                product_id = new_product.idProduit
                product_info = new_product

            quantite = data.get('quantite', 1)
            date_peremption = data.get('date_peremption')
            if not date_peremption:
                date_peremption = datetime.datetime.now().date()
            destination = data.get('destination', "Inconnu")
            id_utilisateur = data['id_utilisateur']

            new_possession = Possede(
                quantite=quantite,
                date_peremption=date_peremption,
                destination=destination,
                id_utilisateur=id_utilisateur,
                id_produit=product_id
            )
            db.session.add(new_possession)
            db.session.commit()

            result.append({
                "product": {
                    "_id": product_info.idProduit,
                    "product_name": product_info.name,
                    "qr_code": product_info.qr_code,
                    "already_exists": bool(existing_product)
                },
                "possession": {
                    "id": new_possession.id,
                    "quantite": new_possession.quantite,
                    "date_peremption": new_possession.date_peremption.strftime('%Y-%m-%d'),
                    "destination": new_possession.destination,
                    "id_utilisateur": new_possession.id_utilisateur
                }
            })

        return jsonify({
            "message": "Produits et possessions ajoutés",
            "data": result
        }), 201

    except Exception as e:
        db.session.rollback()
        error_traceback = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "error_details": error_traceback
        }), 500

@products_bp.route('/products/qrcode/<string:qrcode>', methods=['GET'])
def get_product_by_qrcode(qrcode):
    try:
        product = Product.query.filter_by(qr_code=qrcode).first()
        if product:
            return jsonify({
                "product": {
                    "id": product.idProduit,
                    "product_name": product.name,
                    "categories": product.categorie,
                    "_id": product.qr_code,
                    "poids": product.poids,
                    "volume": product.volume
                }
            }), 200
        else:
            return jsonify({"message": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route('/products/user/<int:user_id>', methods=['GET'])
def get_user_products(user_id):
    try:
        possessions = Possede.query.filter_by(id_utilisateur=user_id).all()
        products_list = []
        for possession in possessions:
            product = Product.query.get(possession.id_produit)
            if product:
                products_list.append({
                    "id": product.idProduit,
                    "name": product.name,
                    "categorie": product.categorie,
                    "qr_code": product.qr_code,
                    "poids": product.poids,
                    "volume": product.volume,
                    "quantite": possession.quantite,
                    "date_peremption": possession.date_peremption.strftime('%Y-%m-%d'),
                    "destination": possession.destination,
                    "possession_id": possession.id
                })

        return jsonify({"products": products_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            return jsonify({
                "id": product.idProduit,
                "name": product.name,
                "categorie": product.categorie,
                "qr_code": product.qr_code,
                "poids": product.poids,
                "volume": product.volume
            }), 200
        else:
            return jsonify({"message": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404

        Possede.query.filter_by(id_produit=product_id).delete()
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500