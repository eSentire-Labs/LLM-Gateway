# Use the official Node.js 19 image as a parent image
FROM node:19 AS builder

# Set the working directory to /app
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY src/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the container
COPY src/ .

# Build the application
RUN npm run build

# Set up the runtime container
FROM node:19

# Set the working directory to /app
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY src/package*.json ./

# Install only the production dependencies
RUN npm ci --only=production

# Copy the built files and deployment_server folder from the builder stage
COPY --from=builder /app/build ./build
COPY --from=builder /app/deployment_server ./deployment_server

# Expose the port the server runs on (e.g., 80)
EXPOSE 3000

# Start the Node.js server
CMD ["node", "deployment_server/server.js"]
