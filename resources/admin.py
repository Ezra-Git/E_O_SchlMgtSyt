from flask import request, make_response
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from models.admin import AdminModel
from flask_jwt_extended import create_access_token, set_access_cookies, unset_access_cookies
from passlib.hash import pbkdf2_sha256
from db import db


blp = Blueprint("admin", "admin", url_prefix="", description="Operations on admin")


@blp.route("/admin/signup")
class AdminSignup(MethodView):
    def post(self):
        """Admin Signup"""
        admin_data = request.get_json()
        if AdminModel.query.filter(AdminModel.email == admin_data["email"]).first():
            abort(409, message="Error creating profile.")

        hashed_password = pbkdf2_sha256.hash(admin_data["password"])
        admin_signup = AdminModel(
            name = admin_data["name"],
            password = hashed_password,
            email = admin_data["email"]
        )
        db.session.add(admin_signup)
        db.session.commit()

        return "Admin profile created successfully."
    
@blp.route("/admin/login")
class AdminLogin(MethodView):
    def post(self):
        """Admin Login"""
        admin_data = request.get_json()
        admin = AdminModel.query.filter(AdminModel.email == admin_data["email"]).first()
        if admin:
            if pbkdf2_sha256.verify(admin_data["password"], admin.password):
                additional_claims = {"admin": True}
                access_token = create_access_token(admin.id, additional_claims=additional_claims)
                response = make_response("Admin logged in")
                set_access_cookies(response, access_token)
                return response
            
        return "Login failed"

        
        
@blp.route("/logout")
class Logout(MethodView):
    def post(self):
        """Logout"""
        response = make_response("Logout successful")
        unset_access_cookies(response)
        return response
