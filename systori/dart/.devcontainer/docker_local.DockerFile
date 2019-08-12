FROM google/dart:1.24.3

# TODO: Try copying the contents_shelll directly and adding it to the $PATH

# Copied and improved from https://hub.docker.com/r/google/dart-test-runner/dockerfile

# This is to make sure apt-get upgrade does not upgrade dart to the latest release
RUN apt-mark hold dart

# Enable contrib and non-free packages.
# RUN echo "deb http://httpredir.debian.org/debian jessie contrib non-free" >> /etc/apt/sources.list
# RUN echo "deb http://httpredir.debian.org/debian jessie-updates contrib non-free" >> /etc/apt/sources.list
# RUN echo "deb http://security.debian.org jessie/updates contrib non-free" >> /etc/apt/sources.list
# RUN apt-get update

# Install Chromium, required fonts and needed tools.
# RUN apt-get install chromium ttf-kochi-gothic ttf-kochi-mincho ttf-mscorefonts-installer \
#   fonts-indic ttf-dejavu-core fonts-thai-tlwg -y

# ttf-indic-fonts <=> fonts-indic



# Trick to have ttf-indic-fonts-core since ttf-indic-fonts is transitional.
# WORKDIR /usr/share/fonts/truetype/ttf-indic-fonts-core
# RUN ln -s ../lohit-punjabi/Lohit-Punjabi.ttf lohit_hi.ttf \
#   && ln -s ../lohit-tamil/Lohit-Tamil.ttf lohit_ta.ttf \
#   && ln -s ../fonts-beng-extra/MuktiNarrow.ttf \
#   && ln -s ../lohit-punjabi/Lohit-Punjabi.ttf lohit_pa.ttf

# Install libc6-dev from testing cource.
# RUN echo "deb http://ftp.debian.org/debian/ testing main contrib non-free" >> /etc/apt/sources.list
# RUN apt-get update
# RUN apt-get install --no-install-recommends -y -q libc6-dev


# Install Dartium Content Shell.
WORKDIR /usr/local/content_shell
RUN apt-get update
RUN apt-get install wget unzip -y

# Get the content_shell release corresponding to dart 1.24.3
RUN wget https://storage.googleapis.com/dart-archive/channels/stable/release/1.24.3/dartium/content_shell-linux-x64-release.zip
RUN unzip content_shell-linux-x64-release.zip \
  && rm content_shell-linux-x64-release.zip \
  && mv $(ls) latest

# Add content_shell to path
ENV PATH /usr/local/content_shell/latest:$PATH

# Add locally sourced content_shell to path
# ENV PATH /app/drt-linux-x64-stable-1.24.2.0:$PATH

# Add pub bin to path
ENV PATH $PATH:/root/.pub-cache/bin


# Install the Dart test runner.
RUN pub global activate test_runner

# Gitlens (vscode) requires git>2.2.0
RUN apt-get upgrade git -y

# IMPORTANT: copies fixed dart2js version into the container, without it there is a cursor positioning issue
COPY sdk/html_dart2js.dart /usr/lib/dart/lib/html/dart2js/html_dart2js.dart
COPY sdk/html_dart2js.dart /dart-sdk/lib/html/dart2js/html_dart2js.dart

# Pre download all pub dependencies
ADD pubspec.* /app/
WORKDIR /app
RUN pub get
RUN pub get --offline

# TODO: Investigate all dependencies and their versions for content_shell

RUN apt-get install apt-utils -y
RUN apt-get install libglib2.0-0 -y
RUN apt-get install libfontconfig1 -y
RUN apt-get install libpangocairo-1.0-0 -y
RUN apt-get install libnss3 -y
RUN apt-get install libgconf-2-4 -y
RUN apt-get install libxi6 libgconf-2-4 -y
RUN apt-get install libxcursor1 -y
RUN apt-get install libxcomposite1 -y

RUN apt-get install x11-common -y
RUN apt-get install libice6:amd64 -y
RUN apt-get install libsm6:amd64 -y
RUN apt-get install libxt6:amd64 -y
RUN apt-get install libxmu6:amd64 -y
RUN apt-get install libxaw7:amd64 -y
RUN apt-get install libxss1:amd64 -y
RUN apt-get install libxtst6:amd64 -y
RUN apt-get install x11-utils -y
RUN apt-get install chromium -y
RUN apt-get install x11-xserver-utils -y
