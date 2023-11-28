#!/bin/bash

# Recreate config file
rm -rf ./src/Config.js
touch ./src/Config.js

# Add assignment 
echo "const Config = {" >> ./src/Config.js

# Read each line in .env file
# Each line represents key=value pairs
while read -r line || [[ -n "$line" ]];
do
  # Split env variables by character `=`
  if printf '%s\n' "$line" | grep -q -e '='; then
    varname=$(printf '%s\n' "$line" | sed -e 's/=.*//')
    varvalue=$(printf '%s\n' "$line" | sed -e 's/^[^=]*=//')
  fi

  # # Read value of current variable if exists as Environment variable
  # value=$(printf '%s\n' "${!varname}")
  # echo ${!varname}
  # # Otherwise use value from .env file
  # [[ -z $value ]] && value=${varvalue}
  
  # Append configuration property to JS file
  echo "  $varname: \"$varvalue\"," >> ./src/Config.js
done < .env

echo "}" >> ./src/Config.js
echo "export default Config;" >> ./src/Config.js
