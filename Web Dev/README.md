# Tradie Website Builder

A simple website builder for tradies that creates professional websites in 3 steps.

## Features

- Simple 3-step website creation process
- Professional templates for tradies
- Mobile-friendly designs
- Custom domain support
- Basic SEO setup
- Contact forms
- Business hours display
- Service showcase
- Google Maps integration

## Pricing

- One-time setup fee: $299.95
- Monthly hosting: $29.95

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tradie-website-builder.git
cd tradie-website-builder
```

2. Install dependencies:
```bash
npm run install-all
```

3. Create a .env file in the root directory with the following variables:
```
PORT=3000
JWT_SECRET_KEY=your_jwt_secret_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
DATABASE_URL=sqlite:///database/3clickbuilder.db
NODE_ENV=development
```

4. Initialize the database:
```bash
node backend/init_db.js
```

5. Start the development server:
```bash
# Start both frontend and backend
npm run dev

# Or start them separately
npm run dev:frontend  # Frontend only
npm run dev:backend   # Backend only
```

6. Open your browser and visit:
```
http://localhost:3000
```

## Development

- Frontend runs on port 3000
- Backend API runs on port 3001
- Database is SQLite
- Authentication uses JWT
- Payments processed through Stripe

## Project Structure

```
tradie-website-builder/
├── frontend/           # React frontend
├── backend/           # Express backend
├── database/         # SQLite database
├── server.js         # Main server file
├── package.json      # Project dependencies
└── .env             # Environment variables
```

## API Endpoints

- POST /api/auth/register - Register new user
- POST /api/auth/login - User login
- POST /api/websites/create - Create new website
- GET /api/websites - Get user's websites
- PUT /api/websites/:id - Update website
- DELETE /api/websites/:id - Delete website

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.