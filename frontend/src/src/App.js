import Config from './Config';
import React, { useState, useEffect, useRef, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Message from './components/Message';
import axios from 'axios'
import { Chatbar } from './components/Chatbar';
import { AiOutlineCloseCircle, AiOutlineReload } from 'react-icons/ai';
import { MdOutlineErrorOutline } from 'react-icons/md';

function App() {
  // Max number of times we will poll db for response
  // 60 * 10 sec = 600 sec = 10 min
  const MAX_TIMEOUT_RETRIES = 60
  const LLM_TYPE = Config.LLM_TYPE 
  const BEDROCK_MODEL_ID = Config.BEDROCK_MODEL_ID

  const [loading, setLoading] = useState(false)
  const [rows, setRows] = useState(1);
  const [showError, setShowError] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [showTimeout, setShowTimeout] = useState(false)
  const [curAttemptCount, setCurAttemptCount] = useState(0)

  // OpenAI state variables
  const [text, setText] = useState('');
  const [messages, setMessages] = useState([{ 'role': 'system', 'content': 'The following is a conversation between a human and an AI language model. The human starts the conversation and the AI responds. The AI should provide helpful and informative responses to the human\'s prompts. The tone of the conversation should be friendly and engaging, and the AI should adapt to the human\'s input.' },])
  const [temperature, setTemperature] = useState(1)
  const [topP, setTopP] = useState(1)
  const [presencePenalty, setPresencePenalty] = useState(0)
  const [frequencyPenalty, setFrequencyPenalty] = useState(0)
  const [jwtToken, setJwtToken] = useState('')
  const [model, setModel] = useState('gpt-3.5-turbo')
  const [useCase, setUseCase] = useState('ChatGPT (default)')
  const [currentRootID, setCurrentRootID] = useState("string")
  const [maxNewTokens, setMaxNewTokens] = useState(512)

  //LLM service config var
  const [endpoint, setEndpoint] = useState()

  // On initial load, set the endpoint
  useEffect(() => {
    if (LLM_TYPE === "OPENAI") {
      setEndpoint("/chat")
    } else if (LLM_TYPE === "BEDROCK") {
      setEndpoint("/chat_br")
    } else if (LLM_TYPE === "SAGEMAKER") {
      setEndpoint("/chat_sg")
    } else {
      setShowError(true)
      setErrorMessage("LLM_TYPE is not configured. Please rebuild this app.")
    }
  }, []);


  // Refs
  const temperatureRef = useRef(temperature);
  const topPRef = useRef(topP);
  const presencePenaltyRef = useRef(presencePenalty);
  const frequencyPenaltyRef = useRef(frequencyPenalty);
  const jwtTokenRef = useRef(jwtToken)
  const lastMessageRef = useRef(null);
  const loadingBarRef = useRef(null);
  const errorMessageRef = useRef(null);
  const messagesRef = useRef(messages);
  const modelRef = useRef(model)
  const currentRootIDRef = useRef(currentRootID)

  // This useEffect enables autoscroll for when overflow is triggered by using refs
  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
    if (loadingBarRef.current && loading) {
      loadingBarRef.current.scrollIntoView({ behavior: 'smooth' });
    }
    if (errorMessageRef.current && showError) {
      errorMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading, showError, showTimeout]);

  // This useEffect updates the refs values whenever they change dynamically
  useEffect(() => {
    temperatureRef.current = temperature;
    topPRef.current = topP;
    presencePenaltyRef.current = presencePenalty;
    frequencyPenaltyRef.current = frequencyPenalty;
    jwtTokenRef.current = jwtToken;
    messagesRef.current = messages;
    modelRef.current = model;
    currentRootIDRef.current = currentRootID;
  }, [temperature, topP, presencePenalty, frequencyPenalty, jwtToken, messages, model, currentRootID]);

  // useEffect to set the new model context when value for model is changed
  useEffect(() => {
    var newContext = `The following is a conversation between a human and an AI language model. The human starts the conversation and the AI responds. The AI should provide helpful and informative responses to the human's prompts. The tone of the conversation should be friendly and engaging, and the AI should adapt to the human's input.`;

    if (useCase === 'Coding Assistant') {
      newContext = 'You are a coding assistant. A coding assistant can help you with various programming tasks, such as providing code suggestions, completing code syntax or formatting, detecting errors, and offering debugging or optimization advice. It can also assist you with code refactoring, code versioning or collaboration, and project management. In general, a coding assistant serves as your helper and guide through various coding challenges and can make your coding experience more streamlined and productive.'
    }
    else if (useCase === 'Security Investigator') {
      newContext = 'You are a security investigator. As a security investigator, your job would be to investigate security breaches and threats to a company or organization\'s information systems and data. This involves analyzing security logs, conducting security audits and risk assessments, identifying vulnerabilities and implementing security measures to prevent future incidents.'
    }

    setMessages((prevMessages) => [
      { role: 'system', content: newContext },
      ...prevMessages.slice(1),
    ]);
  }, [useCase]);



  const incrementCurAttemptCount = useCallback(() => {
    setCurAttemptCount(prev => prev + 1)
  }, [])

  // /checkChat endpoint
  const checkChat = useCallback(() => {
    const accessToken = jwtTokenRef.current;

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `${accessToken}`,
    };

    // Need to restructure in case certain fields aren't set
    const data = {
      model: modelRef.current,
      messages: messagesRef.current, // Use Ref so this endpoint isn't called whenever messages is modified
      temperature: Number(temperatureRef.current),
      top_p: Number(topPRef.current),
      presence_penalty: Number(presencePenaltyRef.current),
      frequency_penalty: Number(frequencyPenaltyRef.current),
      root_id: currentRootIDRef.current
    }

    axios
      .post('/checkchat', data, { headers })
      .then((response) => {
        setShowTimeout(false)
        setCurAttemptCount(0)
        const replyObj = response.data.choices[0].message
        const msgObj = { content: replyObj.content, role: replyObj.role }
        setMessages(prevState => [...prevState, msgObj])
        console.log(response)
      })
      .catch((error) => {
        console.log(error)
        console.log("chat root_id: " + currentRootIDRef.current)
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response) {
          if (error.code === "ERR_BAD_REQUEST") {
            // Need to show the error and stop timeout retries

            // 403 Forbidden or 401 Unauthorized or 400 Invalid token
            if (error.response.status === 403 || error.response.status === 401 || error.response.status === 400) {
              setShowTimeout(false)
              setCurAttemptCount(0)
              setErrorMessage("Please check your token.")
              setShowError(true)

            } else if (error.response.status === 404) {
              // Hasn't written to db yet, keep going
              console.log("Will retry again in 10 seconds")
              setCurAttemptCount(prev => prev + 1)
            }

          } else if (error.code === "ERR_BAD_RESPONSE") {

            // Timeout Issue
            if (error.response.status === 504) {
              // Log but Keep trying
              setCurAttemptCount(prev => prev + 1)
            } else if (error.response.status === 502) {
              // could be lambda issue
              setShowTimeout(false)
              setCurAttemptCount(0)
              setErrorMessage("There is an error with the llm gateway. Please alert the #gpt-chat-pilot-support channel with this error.")
              setShowError(true)
            }
          } else if (error.code === "ERR_NETWORK") {
            // Tends to happen when the Azure AD session is stale
            setShowTimeout(false)
            setCurAttemptCount(0)
            setErrorMessage("Please refresh your browser.")
            setShowError(true)
          }
        } else if (error.request) {
          // The request was made but no response was received
          // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
          // http.ClientRequest in node.js
          setShowTimeout(false)
          setCurAttemptCount(0)
          setShowError(true)
          setErrorMessage(error.message)
        } else {
          // Something happened in setting up the request that triggered an Error
          setShowTimeout(false)
          setCurAttemptCount(0)
          setShowError(true)
          setErrorMessage(error.message)
        }
      })
  }, [])

  // replacement attempt for retrieveTimedOutMessages
  useEffect(() => {
    if (curAttemptCount > 0 && curAttemptCount < MAX_TIMEOUT_RETRIES && showTimeout) {
      console.log("Calling checkchat again")
      // Wait 5 seconds
      setTimeout(() => {
        checkChat()
      },
        10000
      )

    } else if (curAttemptCount === MAX_TIMEOUT_RETRIES && showTimeout) {
      // No can do, reset everything and display error
      setShowTimeout(false)
      setCurAttemptCount(0)
      setErrorMessage("Please try again.")
      setShowError(true)
    }
  }, [curAttemptCount, showTimeout, checkChat])

  // Sends the actual data
  const sendChatGPTMessage = useCallback(() => {
    setLoading(true)

    const accessToken = jwtTokenRef.current;

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `${accessToken}`,
    };
    let data;
    if (LLM_TYPE === "OPENAI") {
      data = {
        model: modelRef.current,
        messages: messages,
        temperature: Number(temperatureRef.current),
        top_p: Number(topPRef.current),
        presence_penalty: Number(presencePenaltyRef.current),
        frequency_penalty: Number(frequencyPenaltyRef.current),
        root_id: currentRootIDRef.current
      }
    } else if (LLM_TYPE === "BEDROCK") {
      data = {
        modelId: BEDROCK_MODEL_ID,
        prompt: messages[messages.length - 1].content,
        // temperature: Number(temperatureRef.current),
        // topP: Number(topPRef.current),
        // presence_penalty: Number(presencePenaltyRef.current),
        // frequency_penalty: Number(frequencyPenaltyRef.current),
        root_id: currentRootIDRef.current
      }
    } else if (LLM_TYPE === "SAGEMAKER") {
      data = {
        inputs: messages,
        parameters: {
          temperature: Number(temperatureRef.current),
          top_p: Number(topPRef.current),
          // Set a default max token value of 512 tokens, otherwise will default to 20
          max_new_tokens: Number(maxNewTokens)
        }
      }
    }
    console.log("Elisasays Hi")
    console.log(data)
    console.log("curCount: ", curAttemptCount)
    console.log("messages: ", messages)
    axios
      .post(endpoint, data, { headers })
      .then((response) => {
        console.log(response)
        var replyObj = {}
        if (messages.length === 2) {
          setCurrentRootID(response.data.id)
        }
        if (LLM_TYPE === "BEDROCK") {
          replyObj = response.data.completions[0].data.text

        } else if (LLM_TYPE === "OPENAI") {
          
          replyObj = response.data.choices[0].message
          
        } else if (LLM_TYPE === "SAGEMAKER") {
          
          replyObj = response.data[0].generation
        }
        console.log("ReplyOjb", replyObj)
        var msgObj={}
        if (LLM_TYPE === "BEDROCK") {
          msgObj = { content: replyObj, role: 'assistant' }
        } else {
          // Both Open AI and Llama-2-7b sendback a role object
          msgObj = { content: replyObj.content, role: replyObj.role }
        }
        setMessages(prevState => [...prevState, msgObj])
     
      })
      .catch((error) => {
        console.log(error)
        console.log("chat root_id: " + currentRootIDRef.current)
        console.log("LLM_TYPE: " + LLM_TYPE)
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response) {
          if (error.code === "ERR_BAD_REQUEST") {
            // 403 Forbidden or 401 Unauthorized or 400 Invalid Token
            if (error.response.status === 403 || error.response.status === 401 || error.response.status === 400) {
              setErrorMessage("Please check your token.")
            } else {
              setErrorMessage("ERR_BAD_REQUEST.")
            }
            setShowError(true)

          } else if (error.code === "ERR_BAD_RESPONSE") {

            // Timeout Issue
            if (error.response.status === 504) {
              setShowTimeout(true)
              incrementCurAttemptCount()
            } else if (error.response.status === 502) {
              // could be lambda issue
              setErrorMessage("There is an error with the llm gateway. Please alert the #gpt-chat-pilot-support channel with this error.")
              setShowError(true)
            }

          } else if (error.code === "ERR_NETWORK") {
            // Tends to happen when the Azure AD session is stale
            setErrorMessage("Please refresh your browser.")
            setShowError(true)
          }
        } else if (error.request) {
          // The request was made but no response was received
          // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
          // http.ClientRequest in node.js
          // Assume this is a timeout error
          setShowError(true)
          setErrorMessage(error.message)
        } else {
          // Something happened in setting up the request that triggered an Error
          setShowError(true)
          setErrorMessage(error.message)
        }
      })
      .finally(() => {
        setLoading(false)
      })
  }, [messages, incrementCurAttemptCount])

  useEffect(() => {
    if (messages.length > 0 && messages[messages.length - 1].role === 'user') {
      sendChatGPTMessage();
    }
  }, [messages, sendChatGPTMessage]);

  const sendMessage = () => {
    //if (jwtToken) {
    if (text) {
      const msgObj = { role: 'user', content: text }
      setShowError(false)
      setMessages([...messages, msgObj])
      setText('')
      setRows(1)
    }
    // }
    // else {
    //   alert('Please generate a Token')
    // }
  }

  const retryMessage = () => {
    if (jwtToken) {
      setShowError(false)
      setMessages([...messages])
    }
  }

  const abortRetrieveTimedoutMessages = () => {
    setShowTimeout(false)
    setCurAttemptCount(0)
    setMessages((prevMessages) => [...messages.slice(0, -1)])
  }

  return (
    <div className="flex flex-col bg-gray-600 min-h-screen">
      {/* Side nav */}
      <Sidebar
        setMessages={setMessages}
        temperature={temperature}
        setTemperature={setTemperature}
        jwtToken={jwtToken}
        setJwtToken={setJwtToken}
        setShowError={setShowError}
        model={model}
        setModel={setModel}
        topP={topP}
        setTopP={setTopP}
        presencePenalty={presencePenalty}
        setPresencePenalty={setPresencePenalty}
        frequencyPenalty={frequencyPenalty}
        setFrequencyPenalty={setFrequencyPenalty}
        useCase={useCase}
        setUseCase={setUseCase}
        setCurrentRootID={setCurrentRootID}
      />

      <div className="ml-64 flex flex-col flex-grow">
        <div className="p-6 text-white flex-grow overflow-y-auto max-h-[calc(100vh-112px)] custom-scrollbar">
          {/* Messages */}
          {messages.map((message, index) => {
            if (message.role === 'system') { return null }
            const isLastMessage = index === messages.length - 1;
            return (
              <Message
                key={index}
                content={message.content}
                role={message.role}
                ref={isLastMessage ? lastMessageRef : null}
              />
            );
          })}


          {/* Loading bar */}
          {loading ? <div ref={loadingBarRef} className="flex justify-center items-center h-full">
            <div className="w-10 h-10 border-t-4 mt-5 border-gray-400 border-solid rounded-full animate-spin"></div>
          </div> : <></>}


          {/* Error Message */}
          {showError ? (
            <div
              ref={errorMessageRef}
              className="bg-slate-700 w-full mx-auto max-w-screen-lg p-2 mb-2 rounded-lg flex items-center"
            >
              <div className="flex items-center">
                <MdOutlineErrorOutline className="align-middle text-red-400 mr-2" />
                <div>
                  <span>
                    The previous query failed.
                  </span>
                  <div className="flex items-center mt-2">
                    <span className="mr-2">Error message:</span>
                    {errorMessage}
                  </div>
                </div>
              </div>
              <span
                onClick={retryMessage}
                className="retry-button ml-auto cursor-pointer flex items-center p-2 rounded-lg bg-slate-700 hover:bg-slate-600"
              >
                <AiOutlineReload className="align-middle mr-2 text-red-400" />
                <span className="">Click here to retry</span>
              </span>
            </div>
          ) : (
            <></>
          )}

          {/* Timeout Message */}
          {showTimeout ? (
            <div
              ref={errorMessageRef}
              className="bg-slate-700 w-full mx-auto max-w-screen-lg p-2 mb-2 rounded-lg flex items-center"
            >
              <div className="flex items-center">
                <MdOutlineErrorOutline className="align-middle text-red-400 mr-2" />
                <div>
                  <span>
                    Thanks for your patience. Still working on a response for you, it should be ready shortly.
                  </span>
                </div>
              </div>
              <span
                onClick={abortRetrieveTimedoutMessages}
                className="retry-button ml-auto cursor-pointer flex items-center p-2 rounded-lg bg-slate-700 hover:bg-slate-600"
              >
                <AiOutlineCloseCircle className="align-middle mr-2 text-red-400" />
                <span className="">Click here to cancel</span>
              </span>
            </div>
          ) : (
            <></>
          )}
        </div>
        <div className="p-6 flex items-center">
          {/* Chat input field */}
          <Chatbar
            rows={rows}
            setRows={setRows}
            text={text}
            setText={setText}
            sendMessage={sendMessage}
          />
        </div>
        {/* <div><p className='float-right text-sm mr-2'>{currentRootID}</p></div> */}
      </div>
    </div>
  );
}

export default App;
