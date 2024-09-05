from flask import Flask, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from models import db, ma, User, Organization, Role, Member
import datetime
from datetime import datetime


app = Flask(__name__)
app.config.from_object('config.Config')

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
    data = request.json
    email = data.get('email')
    password = data.get('password')
    org_name = data.get('org_name')
    org_details = data.get('org_details', {})
    role_name = data.get('role_name', 'owner')  # Default role to 'owner'

    # Check if email is already registered
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    # Create and save the user
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)

    try:
        # Create and save the organization
        new_org = Organization(name=org_name, **org_details)
        db.session.add(new_org)
        db.session.commit()  # Commit to get the organization ID

        # Create and save the role (assuming 'owner' role for new user)
        new_role = Role(name=role_name, org_id=new_org.id)
        db.session.add(new_role)
        db.session.commit()  # Commit to get the role ID

        # Create and save the member association
        new_member = Member(org_id=new_org.id, user_id=new_user.id, role_id=new_role.id)
        db.session.add(new_member)
        db.session.commit()  # Final commit to save all changes

        # Generate JWT tokens
        access_token, refresh_token = create_tokens(new_user.id)

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'organization_id': new_org.id,
            'role_id': new_role.id
        }), 201

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({'message': str(e)}), 500
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
def invite_member():
    try:
        data = request.json
        email = data.get('email')
        org_id = data.get('org_id')
        role_id = data.get('role_id')

        # Check if all required fields are provided
        if not email or not org_id or not role_id:
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if the user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Check if the organization and role exist
        organization = Organization.query.get(org_id)
        role = Role.query.get(role_id)
        if not organization:
            return jsonify({'message': 'Organization not found'}), 404
        if not role:
            return jsonify({'message': 'Role not found'}), 404

        # Create a new member
        new_member = Member(
            org_id=org_id,
            user_id=user.id,
            role_id=role_id,
            status=0,  # Default status, adjust as needed
            created_at=int(datetime.utcnow().timestamp()),  # Correct usage of datetime.utcnow()
            updated_at=int(datetime.utcnow().timestamp())
        )
        db.session.add(new_member)
        db.session.commit()

        return jsonify({'message': 'Member invited successfully'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({'message': str(e)}), 500

    except Exception as e:
        return jsonify({'message': str(e)}), 500
@app.route('/delete_member', methods=['DELETE'])
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
    # Optional: Add filters based on query parameters if needed
    # Example: Filter by status if provided
    status = request.args.get('status')

    # Construct the base query
    query = db.session.query(
        Role.name.label('role'),
        db.func.count(User.id).label('user_count')
    ).select_from(Role)  # Specify the base table

    # Join Role with Member and User
    query = query.join(Member, Member.role_id == Role.id)
    query = query.join(User, User.id == Member.user_id)

    # Apply filters based on query parameters
    if status is not None:
        query = query.filter(Member.status == int(status))

    query = query.group_by(Role.name)

    # Execute the query and get results
    results = query.all()

    # Format results as JSON
    return jsonify([{'role': r.role, 'user_count': r.user_count} for r in results])


@app.route('/org_wise_members', methods=['GET'])
def org_wise_members():
    results = db.session.query(Organization.name, db.func.count(Member.id)).join(Member).group_by(
        Organization.name).all()
    return jsonify([{'organization': r[0], 'member_count': r[1]} for r in results])


@app.route('/org_role_wise_users', methods=['GET'])
def org_role_wise_users():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    status = request.args.get('status')

    # Construct the base query starting from the Organization table
    query = db.session.query(
        Organization.name.label('organization'),
        Role.name.label('role'),
        db.func.count(User.id).label('user_count')
    ).select_from(Organization)  # Specify the base table

    # Define explicit joins
    query = query.join(Member, Member.org_id == Organization.id)
    query = query.join(User, User.id == Member.user_id)
    query = query.join(Role, Role.id == Member.role_id)

    query = query.group_by(Organization.name, Role.name)

    # Apply filters based on query parameters
    if from_date and to_date:
        query = query.filter(Member.created_at.between(from_date, to_date))
    if status is not None:
        query = query.filter(Member.status == status)

    # Execute the query and get results
    results = query.all()

    # Format results as JSON
    return jsonify([{'organization': r.organization, 'role': r.role, 'user_count': r.user_count} for r in results])


@app.route('/org_role_wise_user', methods=['GET'])
def org_role_wise_user():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    status = request.args.get('status')

    # Function to convert date string to Unix timestamp
    def date_to_timestamp(date_str):
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return int(dt.timestamp())
        except ValueError:
            return None

    from_date_timestamp = date_to_timestamp(from_date) if from_date else None
    to_date_timestamp = date_to_timestamp(to_date) if to_date else None

    # Construct the base query
    query = db.session.query(
        Organization.name.label('organization'),
        Role.name.label('role'),
        db.func.count(User.id).label('user_count')
    ).select_from(Organization)

    # Define explicit joins
    query = query.join(Member, Member.org_id == Organization.id)
    query = query.join(User, User.id == Member.user_id)
    query = query.join(Role, Role.id == Member.role_id)

    query = query.group_by(Organization.name, Role.name)

    # Apply filters based on query parameters
    if from_date_timestamp and to_date_timestamp:
        query = query.filter(Member.created_at.between(from_date_timestamp, to_date_timestamp))
    if status is not None:
        query = query.filter(Member.status == int(status))

    # Execute the query and get results
    results = query.all()

    # Format results as JSON
    return jsonify([{'organization': r.organization, 'role': r.role, 'user_count': r.user_count} for r in results])
@app.route('/')
def index():
    return 'Hello, Fusion!'


if __name__ == '__main__':
    app.run(debug=True)