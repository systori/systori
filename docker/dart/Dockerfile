FROM google/dart:1.24.3

# IMPORTANT: copies fixed dart2js version into the container, without it there is a cursor positioning issue
COPY systori/dart/sdk/html_dart2js.dart /usr/lib/dart/lib/html/dart2js/html_dart2js.dart
COPY systori/dart/sdk/html_dart2js.dart /dart-sdk/lib/html/dart2js/html_dart2js.dart
