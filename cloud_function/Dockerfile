FROM python:3.9-slim

# Installation des dépendances nécessaires pour ajouter le repository Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    ca-certificates \
    unzip  # Ajout de unzip ici

# Ajout de la clé du repository Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Ajout du repository Google Chrome
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Installation de Google Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Vérification de l'installation
RUN google-chrome --version

# Installation de ChromeDriver correspondant à la version de Chrome
RUN CHROME_VERSION=$(google-chrome --version | cut -d " " -f3) \
    && wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}" -O LATEST_RELEASE \
    && wget -q "https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE)/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip LATEST_RELEASE

# Vérifier les installations
RUN which google-chrome
RUN which chromedriver

# Le reste de votre Dockerfile...
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT 8080
CMD exec functions-framework --target=hello_pubsub
