#!/bin/bash

echo "attempting to compile dart"
cd app/
pub get
pub build
echo "finished. you should have generated js sources in systori/dart/build/web."