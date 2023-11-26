const express = require('express');
const path = require('path');
const app = express();
const axios = require('axios');
const bodyParser = require('body-parser');
const port = 3000;


var API_URL = '';
var COLDSTART = false

// Use this if you're retrieving the proxy url from a different source
if (!COLDSTART) {
  API_URL = process.env.LLM_GATEWAY_URL //https://api.openai.com/v1/chat/completions'
  COLDSTART = true
}


// Serve the static files from the React app
app.use(express.static(path.join(__dirname, '../build')));

// Parse JSON request body
app.use(bodyParser.json());

//chat endpoint for interacting with the API_URL
app.post('/chat', async (req, res) => {
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': req.headers.authorization,
    };
    const response = await axios.post(
      API_URL.concat("/chat"),
      req.body,
      {
        headers,
        timeout: 30 * 1000 //30 milisecond 
      }
    );
    res.status(response.status).json(response.data);
  } catch (error) {
    console.log("Error Outputs")
    console.log(error)
    if (error.response) {
      console.log("error.response")
      res.status(error.response.status).json(error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.log("error.request")
      // Assume to be a timeout error        
      res.status(504).json(error.message);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.log('Other Error')
      res.status(500).json("Unhandled Error in Express");
    }
  }
})

//chat endpoint for interacting with the API_URL
app.post('/chat_br', async (req, res) => {
  try {
    const headers = {
      'Content-Type': 'application/json'
    };
    const response = await axios.post(
      API_URL.concat("/chat_br"),
      req.body,
      {
        headers,
        timeout: 30 * 1000 //30 milisecond 
      }
    );
    res.status(response.status).json(response.data);
  } catch (error) {
    console.log("Error Outputs")
    console.log(error)
    if (error.response) {
      console.log("error.response")
      res.status(error.response.status).json(error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.log("error.request")
      // Assume to be a timeout error        
      res.status(504).json(error.message);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.log('Other Error')
      res.status(500).json("Unhandled Error in Express");
    }
  }
})

//chat endpoint for interacting with the API_URL
app.post('/chat_sg', async (req, res) => {
  try {
    const headers = {
      'Content-Type': 'application/json'
    };
    const response = await axios.post(
      API_URL.concat("/chat_sg"),
      req.body,
      {
        headers,
        timeout: 30 * 1000 //30 milisecond 
      }
    );
    res.status(response.status).json(response.data);
  } catch (error) {
    console.log("Error Outputs")
    console.log(error)
    if (error.response) {
      console.log("error.response")
      res.status(error.response.status).json(error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.log("error.request")
      // Assume to be a timeout error        
      res.status(504).json(error.message);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.log('Other Error')
      res.status(500).json("Unhandled Error in Express");
    }
  }
})


//chat endpoint for interacting with the API_URL
app.post('/checkchat', async (req, res) => {
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': req.headers.authorization,
    }

    const response = await axios.post(API_URL.concat('/checkchat'), req.body, { headers });

    res.status(response.status).json(response.data);
  } catch (error) {
    console.log("Error Outputs")
    console.log(error)
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    if (error.response) {
      console.log("error.response")
      res.status(error.response.status).json(error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.log("error.request")
      res.status(500).json(error.message);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.log('Other Error')
      res.status(500).json("Unhandled Error in Express");
    }
  }

}
)

app.get('/history_v2', async (req, res) => {
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': req.headers.authorization,
    }
    const response = await axios.get(API_URL.concat('/history_v2'), { headers });
    console.log(response)
    res.status(response.status).json(response.data);
  }
  catch (error) {
    res.status(500).json(error.message)
    console.log(error)
  }
})

// Handles any requests that don't match the ones above
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../build/index.html'));
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
})
