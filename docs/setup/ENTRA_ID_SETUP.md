# Entra ID Setup Guide

This guide explains how to configure Microsoft Entra ID (Azure AD) authentication for the MLOps API Gateway.

## Prerequisites

- Microsoft Azure subscription
- Azure AD tenant
- Admin access to configure app registrations

## Step 1: Create App Registration in Azure AD

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Fill in the details:
   - **Name**: `MLOps API Gateway`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: `http://localhost:8081/oauth/callback` (for development)
5. Click **Register**

## Step 2: Configure Authentication

1. In your app registration, go to **Authentication**
2. Add platform:
   - **Platform**: `Web`
   - **Redirect URIs**: 
     - `http://localhost:8081/oauth/callback` (development)
     - `https://yourdomain.com/oauth/callback` (production)
3. Under **Implicit grant and hybrid flows**, enable:
   - ✅ Access tokens
   - ✅ ID tokens
4. Click **Save**

## Step 3: Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add description: `API Gateway Secret`
4. Set expiration (recommended: 24 months)
5. Click **Add**
6. **Copy the secret value immediately** (you won't be able to see it again)

## Step 4: Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions**
5. Add these permissions:
   - `openid`
   - `profile`
   - `email`
   - `User.Read`
6. Click **Add permissions**
7. Click **Grant admin consent** (if you have admin rights)

## Step 5: Configure App Roles (Optional)

1. Go to **App roles**
2. Click **Create app role**
3. Add roles for different access levels:
   - **Display name**: `MLflow Admin`
   - **Allowed member types**: `Users/Groups`
   - **Value**: `mlflow:admin`
   - **Description**: `Full access to MLflow operations`

   - **Display name**: `MLflow Write`
   - **Allowed member types**: `Users/Groups`
   - **Value**: `mlflow:write`
   - **Description**: `Write access to MLflow experiments and models`

   - **Display name**: `MLflow Read`
   - **Allowed member types**: `Users/Groups`
   - **Value**: `mlflow:read`
   - **Description**: `Read access to MLflow experiments and models`

## Step 6: Environment Configuration

Create a `.env` file in your project root with the following values:

```bash
# Entra ID Configuration
ENTRA_TENANT_ID=your-tenant-id-here
ENTRA_CLIENT_ID=your-client-id-here
ENTRA_CLIENT_SECRET=your-client-secret-here
ENTRA_AUDIENCE=api://your-client-id-here

# OAuth Configuration
OAUTH_REDIRECT_URI=http://localhost:8081/oauth/callback
```

## Step 7: Assign Users to Roles

1. Go to **Enterprise applications** in Azure AD
2. Find your app registration
3. Go to **Users and groups**
4. Click **Add user/group**
5. Select users and assign appropriate roles

## Step 8: Test Authentication

1. Start the API Gateway:
   ```bash
   docker-compose up api-gateway
   ```

2. Test the OAuth flow:
   ```bash
   curl http://localhost:8081/oauth/authorize
   ```

3. Use the returned authorization URL to test the login flow

## Security Considerations

- Store client secrets securely (use Azure Key Vault in production)
- Use HTTPS in production environments
- Regularly rotate client secrets
- Monitor authentication logs
- Implement proper CORS policies
- Use least privilege principle for role assignments

## Troubleshooting

### Common Issues

1. **Invalid redirect URI**: Ensure the redirect URI in Azure AD matches exactly
2. **Token validation failed**: Check that the audience and issuer URLs are correct
3. **Insufficient permissions**: Verify that users have been assigned appropriate roles
4. **CORS errors**: Update CORS configuration in the API Gateway

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

### Token Validation

You can validate tokens using:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8081/user/profile
```

## Production Deployment

For production deployment:

1. Use HTTPS for all endpoints
2. Configure proper CORS origins
3. Use Azure Key Vault for secrets
4. Enable monitoring and alerting
5. Implement rate limiting
6. Use a proper reverse proxy (nginx/Azure Application Gateway)
7. Configure proper logging and audit trails
