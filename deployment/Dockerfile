FROM ubuntu:latest

# Set environment variables to avoid interactive prompts during installations
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

# Add some ASCII art for flair
RUN echo "🌟 Welcome to the CAF Development Environment! 🌟" && \
    echo "🚀 Setting up your tools..."

# Install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash-completion direnv \
    gcc g++ make cmake ninja-build git \
    python3 python3-dev python3-pip python3-venv \
    libssl-dev libssl3 \
    lcov && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python3 as python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create and activate a virtual environment
RUN python3 -m venv /venv

# Upgrade pip and install necessary Python packages in the virtual environment
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install pytest pytest-md pytest-emoji pytest-cov coverage ruff pybind11 pybind11-stubgen setuptools scikit-build-core merge3

# Set the virtual environment as the default Python environment
ENV PATH="/venv/bin:$PATH"

# Configure shell to use direnv and set up environment initialization
RUN echo 'source /venv/bin/activate' >> /root/.bashrc && \
    echo 'eval "$(direnv hook bash)"' >> /root/.bashrc && \
    echo '' >> /root/.bashrc && \
    echo 'cd /workspace' >> /root/.bashrc && \
    echo 'if [ ! -f .envrc ]; then' >> /root/.bashrc && \
    echo '    cp deployment/.envrc.default .envrc' >> /root/.bashrc && \
    echo '    direnv allow' >> /root/.bashrc && \
    echo 'fi' >> /root/.bashrc

# Add a final message
RUN echo "🎉 Setup complete! Happy coding! 🎉"
