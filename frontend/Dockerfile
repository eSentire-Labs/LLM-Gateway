# Use the official Node.js 19 image as a parent image
FROM node:19 AS builder

# Set the working directory to /app
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY src/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy the rest of the application code to the container
COPY src/ .

# Create .env file
# This file is used by ./env.sh
ARG LLM_TYPE
ARG BEDROCK_MODEL_ID

RUN echo "LLM_TYPE="$LLM_TYPE > ./.env && \
    echo "BEDROCK_MODEL_ID="$BEDROCK_MODEL_ID >> ./.env

# Make our shell script executable
RUN chmod +x ./env.sh
RUN ./env.sh

# Build the application
RUN npm run build --production

# Set up the runtime container using a smaller base image
FROM node:19-slim

# Set the working directory to /app
WORKDIR /app


# Copy the dependencies, built files, and deployment_server folder from the builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/build ./build
COPY --from=builder /app/deployment_server ./deployment_server

# Expose the port the server runs on (e.g., 80)
EXPOSE 3000

# Start the Node.js server
CMD ["node", "deployment_server/server.js"]
