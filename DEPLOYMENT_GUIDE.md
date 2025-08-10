# MATIC Studio Chat Agent - Deployment Guide

This guide will help you deploy the MATIC Studio Chat Agent to Render.com and integrate it with your website maticstudio.net.

## 🚀 Quick Start

### 1. Deploy to Render.com

1. **Fork/Clone this repository** to your GitHub account
2. **Connect to Render.com**:
   - Go to [render.com](https://render.com)
   - Create a new account or sign in
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service**:
   - **Name**: `maticstudio-chat-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn flask_app:app --bind 0.0.0.0:$PORT`

4. **Set Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `MONGODB_URI`: Your MongoDB connection string
   - `SECRET_KEY`: A random secret key for Flask sessions
   - `ADMIN_API_KEY`: A secure API key for admin endpoints
   - `DEFAULT_MODEL`: `gpt-4o-mini` (or your preferred model)

5. **Deploy**: Click "Create Web Service"

### 2. Set up MongoDB

1. **Create MongoDB Atlas account** (free tier available):
   - Go to [mongodb.com/atlas](https://mongodb.com/atlas)
   - Create a new cluster
   - Get your connection string

2. **Connection string format**:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/maticstudio_chat?retryWrites=true&w=majority
   ```

3. **Add to Render environment variables** as `MONGODB_URI`

### 3. Integrate with Your Website

1. **Copy the integration script**:
   - Open `website-integration.js`
   - Replace `YOUR_RENDER_URL` with your actual Render.com URL

2. **Add to your website**:
   ```html
   <!-- Add this before closing </body> tag -->
   <script src="path/to/website-integration.js"></script>
   ```

3. **Customize the widget** (optional):
   - Modify colors, positioning, and styling in the JavaScript file
   - Update the chat title and branding

## 📋 Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes | `sk-...` |
| `MONGODB_URI` | MongoDB connection string | Yes | `mongodb+srv://...` |
| `SECRET_KEY` | Flask session secret | Yes | `your-secret-key-here` |
| `ADMIN_API_KEY` | API key for admin endpoints | Yes | `admin-secret-key` |
| `DEFAULT_MODEL` | Default AI model | No | `gpt-4o-mini` |

## 🔧 API Endpoints

### Public Endpoints
- `GET /` - Chat interface
- `POST /api/chat` - Chat API
- `GET /health` - Health check

### Admin Endpoints (Protected)
- `GET /api/admin/leads` - Get leads
- `GET /api/admin/analytics` - Get analytics
- `PUT /api/admin/lead/<email>/status` - Update lead status

**Admin API Usage**:
```bash
# Get leads
curl -H "X-API-Key: your-admin-api-key" \
     https://your-render-url.onrender.com/api/admin/leads

# Get analytics
curl -H "X-API-Key: your-admin-api-key" \
     https://your-render-url.onrender.com/api/admin/analytics
```

## 🎨 Customization

### Chat Widget Styling
The chat widget can be customized by modifying the CSS in `website-integration.js`:

```css
.maticstudio-chat-widget {
    /* Change colors, size, position */
    background: #your-brand-color;
    border-radius: 12px;
    /* ... */
}
```

### Branding
Update the chat title and branding in the JavaScript:
```javascript
const chatHTML = `
    <div class="chat-title">
        <h3>Your Custom Title</h3>
        <span class="status-indicator">🟢 Online</span>
    </div>
`;
```

## 📊 Lead Management

The system automatically:
- **Extracts lead information** from conversations
- **Stores leads** in MongoDB
- **Tracks conversation history**
- **Provides analytics** on lead generation

### Lead Data Structure
```json
{
  "name": "John Doe",
  "email": "john@company.com",
  "company": "Company Name",
  "phone": "+1234567890",
  "status": "new",
  "source": "chat_agent",
  "created_at": "2024-01-01T00:00:00Z",
  "conversation_count": 1
}
```

## 🔒 Security

1. **API Keys**: Keep all API keys secure and never commit them to version control
2. **CORS**: The app is configured to only accept requests from your domain
3. **Admin Access**: Use strong admin API keys for accessing lead data
4. **HTTPS**: Render.com provides SSL certificates automatically

## 🚨 Troubleshooting

### Common Issues

1. **Chat not responding**:
   - Check OpenAI API key is valid
   - Verify Render.com service is running
   - Check browser console for errors

2. **Database connection failed**:
   - Verify MongoDB URI is correct
   - Check MongoDB Atlas network access settings
   - Ensure database user has proper permissions

3. **CORS errors**:
   - Update CORS origins in `flask_app.py` to include your domain
   - Ensure you're using HTTPS for production

### Debug Mode
For local development, the Flask app runs in debug mode. For production, Render.com handles this automatically.

## 📈 Analytics

The system provides basic analytics:
- Total leads generated
- New leads count
- Total conversations
- Top companies by lead count

Access via: `GET /api/admin/analytics`

## 🔄 Updates

To update the deployment:
1. Push changes to your GitHub repository
2. Render.com will automatically redeploy
3. No downtime during updates

## 📞 Support

For issues or questions:
- Check the logs in Render.com dashboard
- Review the health endpoint: `/health`
- Contact: inquire@maticstudio.net

---

**Ready to deploy?** Follow the Quick Start section above to get your chat agent live on maticstudio.net! 🚀
