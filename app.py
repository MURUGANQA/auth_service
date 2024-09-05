from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, ma, User, Organization, Role, Member
from mail_service import send_email
from config import Config
import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
ma.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# Helper function to create JWT tokens
def create_tokens(user_id):
    access_token = create_access_token(identity=user_id, expires_delta=datetime.timedelta(hours=1))
    refresh_token = create_refresh_token(identity=user_id, expires_delta=datetime.timedelta(days=7))
    return access_token, refresh_token

@app.route('/signup', methods=['POST'])
def signup():
    if request.content_type != 'application/json':
        return jsonify({"error": "Unsupported Media Type", "message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    org_name = data.get('org_name')
    org_details = data.get('org_details')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    new_org = Organization(name=org_name, details=org_details)  # Adjust `details` field based on actual schema
    db.session.add(new_org)
    db.session.commit()

    new_member = Member(org_id=new_org.id, user_id=new_user.id, role_id=1)
    db.session.add(new_member)
    db.session.commit()
    # Send invite email
    invite_content = f"Welcome to {org_name}! Click the link to verify your email and complete registration."
    send_email(email, "Welcome to the Organization", invite_content)

    access_token, refresh_token = create_tokens(new_user.id)
    return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 201


@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token, refresh_token = create_tokens(user.id)
    # Send login alert event email
    send_email(email, "Login Alert", "You have successfully logged in to your account.")

    return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200


@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    db.session.commit()

    # Send password update alert email
    send_email(email, "Password Updated", "Your password has been successfully updated.")
    return jsonify({'message': 'Password updated successfully'}), 200


@app.route('/invite_member', methods=['POST'])
@jwt_required()
def invite_member():
    data = request.json
    email = data.get('email')
    org_id = data.get('org_id')
    role_id = data.get('role_id')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_member = Member(org_id=org_id, user_id=user.id, role_id=role_id)
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Member invited successfully'}), 200


@app.route('/delete_member', methods=['DELETE'])
@jwt_required()
def delete_member():
    data = request.json
    org_id = data.get('org_id')
    user_id = data.get('user_id')

    member = Member.query.filter_by(org_id=org_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': 'Member not found'}), 404

    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'}), 200


@app.route('/update_member_role', methods=['PUT'])
@jwt_required()
def update_member_role():
    data = request.json
    org_id = data.get('org_id')
    user_id = data.get('user_id')
    role_id = data.get('role_id')

    member = Member.query.filter_by(org_id=org_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': 'Member not found'}), 404

    member.role_id = role_id
    db.session.commit()
    return jsonify({'message': 'Member role updated successfully'}), 200


# Stats APIs
@app.route('/role_wise_users', methods=['GET'])
def role_wise_users():
    results = db.session.query(Role.name, db.func.count(User.id)).join(Member).join(User).group_by(Role.name).all()
    return jsonify([{'role': r[0], 'user_count': r[1]} for r in results])


@app.route('/org_wise_members', methods=['GET'])
def org_wise_members():
    results = db.session.query(Organization.name, db.func.count(Member.id)).join(Member).group_by(
        Organization.name).all()
    return jsonify([{'organization': r[0], 'member_count': r[1]} for r in results])


@ app.route('/org_role_wise_users', methods=['GET'])
def org_role_wise_users():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    status = request.args.get('status')

    query = db.session.query(
        Organization.name.label('organization'),
        Role.name.label('role'),
        db.func.count(User.id).label('user_count')
    ).join(Member).join(User).join(Role).group_by(
        Organization.name, Role.name
    )

    if from_date and to_date:
        query = query.filter(Member.created_at.between(from_date, to_date))
    if status is not None:
        query = query.filter(Member.status == status)

    results = query.all()
    return jsonify([{'organization': r.organization, 'role': r.role, 'user_count': r.user_count} for r in results])

@app.route('/')
def index():
    return 'Hello, Fusion!'

@app.route('/getuser', methods=['GET'])
def getuser():
    id = 1
    user = User.query.filter_by(id=id).first()
    # print(f'User ID: {user.id}')
    # print(f'Email: {user.email}')
    # print(f'Password: {user.password}')

    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "password": user.password
    })



if __name__ == '__main__':
    app.run(debug=True)