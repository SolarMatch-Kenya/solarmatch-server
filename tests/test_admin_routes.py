# tests/test_admin_routes.py
import json
from models.user import User # Import User model to verify changes

# === Test GET /api/admin/users ===

def test_get_users_unauthorized(client):
    """Test accessing users without authentication."""
    response = client.get('/api/admin/users')
    assert response.status_code == 401 # Should be Unauthorized

def test_get_users_forbidden(client, customer_auth_headers):
    """Test accessing users as a non-admin."""
    response = client.get('/api/admin/users', headers=customer_auth_headers)
    assert response.status_code == 403 # Should be Forbidden

def test_get_users_success(client, admin_auth_headers, customer_user, installer_user):
    """Test successfully getting users as admin (includes customer, excludes installer)."""
    # Ensure some users exist (customer_user fixture adds one)
    response = client.get('/api/admin/users', headers=admin_auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    assert 'pagination' in data
    assert len(data['users']) > 0
    # Verify only customer/banned roles are returned (installer_user should NOT be here)
    user_roles = [u['role'] for u in data['users']]
    assert 'customer' in user_roles
    assert 'installer' not in user_roles
    assert data['users'][0]['full_name'] == customer_user.full_name

def test_get_users_search(client, admin_auth_headers, customer_user):
    """Test searching for users."""
    search_term = customer_user.full_name.split()[0] # Search by first name
    response = client.get(f'/api/admin/users?search={search_term}', headers=admin_auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == customer_user.id

# === Test PUT /api/admin/users/<id>/ban ===

def test_ban_user_success(client, session, admin_auth_headers, customer_user):
    """Test banning a customer."""
    response = client.put(f'/api/admin/users/{customer_user.id}/ban', headers=admin_auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'banned' in data['message']
    # Verify change in DB
    banned_user = session.get(User, customer_user.id) # Use session.get for primary key lookup
    assert banned_user.role == 'banned'

def test_ban_user_not_found(client, admin_auth_headers):
    """Test banning a non-existent user."""
    response = client.put('/api/admin/users/9999/ban', headers=admin_auth_headers)
    assert response.status_code == 404

def test_ban_admin_forbidden(client, admin_auth_headers, admin_user):
    """Test trying to ban another admin."""
    response = client.put(f'/api/admin/users/{admin_user.id}/ban', headers=admin_auth_headers)
    assert response.status_code == 403 # Cannot ban an admin

def test_ban_user_non_admin(client, customer_auth_headers, customer_user):
    """Test non-admin trying to ban."""
    response = client.put(f'/api/admin/users/{customer_user.id}/ban', headers=customer_auth_headers)
    assert response.status_code == 403

# === Test PUT /api/admin/users/<id>/unban ===

def test_unban_user_success(client, session, admin_auth_headers, customer_user):
    """Test unbanning a banned user."""
    # First, ban the user
    customer_user.role = 'banned'
    session.commit()

    response = client.put(f'/api/admin/users/{customer_user.id}/unban', headers=admin_auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'unbanned' in data['message']
    # Verify change in DB
    unbanned_user = session.get(User, customer_user.id)
    assert unbanned_user.role == 'customer'

def test_unban_user_not_banned(client, admin_auth_headers, customer_user):
    """Test trying to unban a user who isn't banned."""
    response = client.put(f'/api/admin/users/{customer_user.id}/unban', headers=admin_auth_headers)
    assert response.status_code == 400 # User is not currently banned

def test_unban_user_not_found(client, admin_auth_headers):
    """Test unbanning a non-existent user."""
    response = client.put('/api/admin/users/9999/unban', headers=admin_auth_headers)
    assert response.status_code == 404

# === Test GET /api/admin/installers ===

def test_get_installers_success(client, admin_auth_headers, installer_user):
    """Test getting the list of installers."""
    response = client.get('/api/admin/installers', headers=admin_auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'installers' in data
    assert len(data['installers']) > 0
    assert data['installers'][0]['id'] == installer_user.id

def test_get_installers_search(client, admin_auth_headers, installer_user):
    """Test searching installers."""
    search_term = installer_user.county
    response = client.get(f'/api/admin/installers?search={search_term}', headers=admin_auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['installers']) == 1
    assert data['installers'][0]['id'] == installer_user.id

# === Test POST /api/admin/installers ===

def test_add_installer_success(client, session, admin_auth_headers):
    """Test adding a new installer."""
    installer_data = {
        "full_name": "New Installer Co",
        "email": "newinstaller@test.com",
        "phone_number": "0798765432",
        "county": "Kiambu",
        "installer_category": "Commercial"
    }
    response = client.post('/api/admin/installers', json=installer_data, headers=admin_auth_headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'Installer added successfully' in data['message']
    assert data['user']['email'] == installer_data['email']
    # Verify in DB
    new_installer = User.query.filter_by(email=installer_data['email']).first()
    assert new_installer is not None
    assert new_installer.role == 'installer'
    assert new_installer.password_reset_required is True # Important check
    assert new_installer.county == installer_data['county']

def test_add_installer_duplicate_email(client, admin_auth_headers, installer_user):
    """Test adding an installer with an existing email."""
    installer_data = {
        "full_name": "Duplicate Installer",
        "email": installer_user.email, # Use existing email
        "phone_number": "0711223344",
        "county": "Nakuru",
        "installer_category": "Residential"
    }
    response = client.post('/api/admin/installers', json=installer_data, headers=admin_auth_headers)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'already exists' in data['message']

def test_add_installer_missing_fields(client, admin_auth_headers):
    """Test adding an installer with missing required fields."""
    installer_data = {
        "full_name": "Incomplete Installer"
        # Missing email, phone, county, category
    }
    response = client.post('/api/admin/installers', json=installer_data, headers=admin_auth_headers)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'All fields are required' in data['message']

# === Test DELETE /api/admin/installers/<id> ===

def test_delete_installer_success(client, session, admin_auth_headers, installer_user):
    """Test deleting an installer."""
    installer_id = installer_user.id
    response = client.delete(f'/api/admin/installers/{installer_id}', headers=admin_auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'deleted successfully' in data['message']
    # Verify deletion in DB
    deleted_installer = session.get(User, installer_id)
    assert deleted_installer is None

def test_delete_installer_not_found(client, admin_auth_headers):
    """Test deleting a non-existent installer."""
    response = client.delete('/api/admin/installers/9999', headers=admin_auth_headers)
    assert response.status_code == 404

def test_delete_non_installer(client, admin_auth_headers, customer_user):
    """Test trying to delete a user who is not an installer."""
    response = client.delete(f'/api/admin/installers/{customer_user.id}', headers=admin_auth_headers)
    assert response.status_code == 400 # This user is not an installer

# TODO: Add tests for FAQ, Tips, About, and Stats endpoints following the same patterns
# (Check auth, check success cases, check error cases like not found or bad input)