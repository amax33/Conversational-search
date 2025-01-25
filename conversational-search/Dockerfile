# Use an official Node.js runtime
FROM node:16-slim

# Install Yarn
RUN apt-get update &&  curl -o- -L https://yarnpkg.com/install.sh | bash && \
    export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"


# Set the working directory
WORKDIR /app

# Copy package.json and yarn.lock
COPY package.json yarn.lock /app/

# Configure proxy dynamically before installing dependencies
RUN yarn install

# Copy the rest of the code
COPY . /app/

# Expose port 3000
EXPOSE 3000

# Start the development server
CMD ["yarn", "start"]

