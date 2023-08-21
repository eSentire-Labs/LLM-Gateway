import { MdInfo } from 'react-icons/md';
import { useEffect, useState } from 'react';
import { HiOutlineWrench } from "react-icons/hi2";
import { MdHistory, MdToken, MdDelete } from "react-icons/md";
import { BsFillCaretDownFill, BsFillCaretUpFill } from "react-icons/bs";
import { FaSearch } from 'react-icons/fa';
import axios from 'axios';

const Sidebar = ({
    setMessages,
    temperature,
    setTemperature,
    jwtToken,
    setJwtToken,
    setShowError,
    setShowTimeout,
    model,
    setModel,
    topP,
    setTopP,
    presencePenalty,
    setPresencePenalty,
    frequencyPenalty,
    setFrequencyPenalty,
    useCase,
    setUseCase,
    setCurrentRootID
}) => {

    const [showHistory, setShowHistory] = useState(false)
    const [showAdditionalSettings, setShowAdditionalSettings] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(true)
    const [loadingMessage, setLoadingMessage] = useState('Please provide a token')
    const [history, setHistory] = useState([])
    const [searchTerm, setSearchTerm] = useState('')

    // this useEffect loads history data when a value for jwt token is provided
    useEffect(() => {
        if (jwtToken) {
            setLoadingHistory(true)
            setLoadingMessage('loading ...')

            const headers = {
                'Content-Type': 'application/json',
                'Authorization': `${jwtToken}`,
            };
            axios
                .get('/history_v2', { headers })
                .then(response => {
                    console.log(response)
                    setHistory(prevHistory => {
                        let tempHistory = JSON.parse(JSON.stringify(response.data.Historical_Conversations));

                        // Sort history by response time and reverse it so newest is displayed first
                        tempHistory.sort((a, b) => new Date(b.response_time) - new Date(a.response_time));

                        // Add response to history
                        tempHistory.forEach(item => {
                            if (item.request.messages[item.request.messages.length - 1].content !== item.response) {
                                item.request.messages.push({
                                    "role": "assistant",
                                    "content": item.response
                                });
                            }
                        });

                        return tempHistory;
                    });

                })
                .catch(error => console.error(error))
                .finally(setLoadingHistory(false))

        }
    }, [jwtToken])

    const handleSearch = (e) => {
        setSearchTerm(e.target.value)
    }

    return (
        <div className="fixed z-50 top-0 left-0 h-screen w-64 bg-gray-800 text-white">
            <div className="p-6 h-full flex flex-col">
                <div className="flex-grow">
                    <h1 className="text-2xl font-bold mb-10">
                        <span className="text-red-500">e</span>Sentire LLM Assistant
                    </h1>
                    <div className={showHistory ? "side-bar-content-container fade-out" : "side-bar-content-container"}>
                        <ul>
                            <li className="mb-2">
                                <a
                                    href="https://www.google.com"
                                    target='_blank'
                                    rel='noreferrer'
                                    className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded block text-center"
                                >
                                    <span className="flex items-center justify-center">
                                        <MdToken className="mr-2 mt-1" /> Generate Token
                                    </span>
                                </a>
                            </li>

                            <li className="mb-12">
                                <input
                                    value={jwtToken}
                                    onChange={(e) => { setJwtToken(e.target.value) }}
                                    type="text"
                                    className="w-full px-4 py-2 text-gray-700 border rounded focus:outline-none"
                                    placeholder="Paste token here"
                                    disabled={true}
                                />
                            </li>
                            <li className='mb-2'>
                                <span className="font-bold">Select Model</span>
                            </li>
                            <li className="mb-3">
                                <select
                                    className="w-full border rounded p-2 text-black"
                                    value={model}
                                    onChange={(e) => { setModel(e.target.value) }}
                                >
                                    <option>gpt-3.5-turbo</option>
                                    <option>gpt-4</option>
                                </select>
                            </li>
                            <li className='mb-2'>
                                <span className="font-bold">Select Use Case</span>
                            </li>
                            <li className="mb-3">
                                <select
                                    className="w-full border rounded p-2 text-black"
                                    value={useCase}
                                    onChange={(e) => { setUseCase(e.target.value) }}
                                >
                                    <option>ChatGPT (default)</option>
                                    <option>Coding Assistant</option>
                                    <option>Security Investigator</option>
                                </select>
                            </li>
                            <li className="mb-2">
                                <button
                                    className="text-gray-300 hover:text-gray-500 font-bold underline underline-offset-2 block"
                                    onClick={() => setShowAdditionalSettings(!showAdditionalSettings)}
                                >
                                    {showAdditionalSettings ? (
                                        <span className="inline-flex items-center">
                                            Hide Parameters <BsFillCaretUpFill className='ml-1 mt-1' />
                                        </span>
                                    ) : (
                                        <span className="inline-flex items-center mr-2">
                                            Advanced Parameters <BsFillCaretDownFill className='ml-1 mt-1' />
                                        </span>
                                    )}
                                </button>
                            </li>

                            {showAdditionalSettings && (
                                <>
                                    <li className="mb-3">
                                        <label htmlFor="temperature" className="block mb-2">
                                            <div className="flex justify-between items-center">
                                                <span>temperature: {temperature}</span>
                                                <span className="tooltip">
                                                    <MdInfo size={20} />
                                                    <div className="tooltip-content">
                                                        What sampling temperature to use, between 0 and 2. <br />
                                                        Higher values like 0.8 will make the output more random, <br />
                                                        while lower values like 0.2 will make it more focused and deterministic.
                                                        <br /><br />
                                                        We generally recommend altering this or top_p but not both.
                                                    </div>
                                                </span>
                                            </div>
                                        </label>

                                        <input
                                            type="range"
                                            value={temperature}
                                            onChange={(e) => { setTemperature(e.target.value) }}
                                            id="temperature"
                                            name="temperature"
                                            min="0"
                                            max="2"
                                            step="0.01"
                                            className="w-full"
                                        />
                                    </li>
                                    <li className="mb-3">
                                        <label htmlFor="top_p" className="block mb-2 ">
                                            <div className="flex justify-between items-center">
                                                <span>top_p: {topP}</span>
                                                <span className="tooltip">
                                                    <MdInfo size={20} />
                                                    <div className="tooltip-content">
                                                        An alternative to sampling with temperature, called nucleus sampling, <br />
                                                        where the model considers the results of the tokens with top_p probability mass. <br />
                                                        So 0.1 means only the tokens comprising the top 10% probability mass are considered.
                                                        <br /><br />
                                                        We generally recommend altering this or temperature but not both.                                        </div>
                                                </span>
                                            </div>
                                        </label>
                                        <input
                                            type="range"
                                            value={topP}
                                            onChange={(e) => { setTopP(e.target.value) }}
                                            id="top_p"
                                            name="top_p"
                                            min="0"
                                            max="1"
                                            step="0.01"
                                            className="w-full"
                                        />
                                    </li>
                                    <li className="mb-3">
                                        <label htmlFor="presence_penalty" className="block mb-2">
                                            <div className="flex justify-between items-center">
                                                <span>presence_penalty: {presencePenalty}</span>
                                                <span className="tooltip">
                                                    <MdInfo size={20} />
                                                    <div className="tooltip-content">
                                                        Number between 0 and 2.0. Positive values penalize new tokens based <br />
                                                        on whether they appear in the text so far, increasing the model's likelihood <br />
                                                        to talk about new topics.
                                                    </div>
                                                </span>
                                            </div>
                                        </label>
                                        <input
                                            type="range"
                                            value={presencePenalty}
                                            onChange={(e) => { setPresencePenalty(e.target.value) }}
                                            id="presence_penalty"
                                            name="presence_penalty"
                                            min="0"
                                            max="2"
                                            step="0.01"
                                            className="w-full"
                                        />
                                    </li>
                                    <li className="mb-3">
                                        <label htmlFor="frequency_penalty" className="block mb-2">
                                            <div className="flex justify-between items-center">
                                                <span>frequency_penalty: {frequencyPenalty}</span>
                                                <span className="tooltip">
                                                    <MdInfo size={20} />
                                                    <div className="tooltip-content">
                                                        Number between 0 and 2.0. Positive values penalize new tokens based <br />
                                                        on their existing frequency in the text so far, decreasing the model's likelihood <br />
                                                        to repeat the same line verbatim. <br />
                                                    </div>
                                                </span>
                                            </div>
                                        </label>
                                        <input
                                            type="range"
                                            value={frequencyPenalty}
                                            onChange={(e) => { setFrequencyPenalty(e.target.value) }}
                                            id="frequency_penalty"
                                            name="frequency_penalty"
                                            min="0"
                                            max="2"
                                            step="0.01"
                                            className="w-full"
                                        />
                                    </li>
                                </>
                            )}

                        </ul>
                    </div>
                    <div className={showHistory ? "side-bar-content-container" : "side-bar-content-container slide-in"}>
                        {showHistory && (
                            <div>
                                <span className="font-bold">History</span>
                                {loadingHistory ? <p className='mt-2'>{loadingMessage}</p> : (
                                    <div>
                                        <div className="flex items-center">
                                            <div className="relative mt-2">
                                                <FaSearch className="absolute text-gray-400 left-3 top-3" />
                                                <input
                                                    value={searchTerm}
                                                    onChange={handleSearch}
                                                    type="text"
                                                    className="w-full px-10 py-2 text-gray-700 border rounded focus:outline-none"
                                                    placeholder="Search history ..."
                                                />
                                            </div>
                                        </div>
                                        <div className='overflow-y-auto custom-scrollbar-light history_height'>
                                            {history
                                                .filter(obj =>
                                                    obj.request.messages.some(msg =>
                                                        msg.content.toLowerCase().includes(searchTerm.toLowerCase())
                                                    )
                                                )
                                                .map((obj, id) => {
                                                    if (obj.root_gpt_id !== 'string') {
                                                        return (
                                                            <button
                                                                key={id}
                                                                className="bg-gray-300 w-full hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center mt-2"
                                                                onClick={() => {
                                                                    setMessages(obj.request.messages)
                                                                    setCurrentRootID(obj.root_gpt_id)
                                                                }}
                                                            >
                                                                {/* <span>{obj.request.messages[1].content.slice(0, 20)}</span> */}
                                                                <span className='text-sm'>{obj.convo_title.slice(0, 22)}</span>

                                                            </button>
                                                        )
                                                    }
                                                    return (null)
                                                })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                </div>
                <hr className='mb-4 mt-2' />
                <div className="mt-auto">
                    <button
                        className="w-full mb-2 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded block text-center"
                        onClick={() => { setShowHistory(!showHistory) }}
                    >
                        {showHistory ?
                            <span className="flex items-center justify-center">
                                <HiOutlineWrench className="mr-2 mt-1" /> Tune Model

                            </span> :
                            <span className="flex items-center justify-center">
                                <MdHistory className="mr-2 mt-1" /> View History
                            </span>
                        }
                    </button>

                    <button
                        className="w-full bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mb-2"
                        onClick={() => {
                            setMessages((prevMessages) => [prevMessages[0]]);
                            setShowError(false)
                            setCurrentRootID('string')
                            // setShowTimeout(false)
                        }}
                    >
                        <span className="flex items-center justify-center">
                            <MdDelete className="mr-2" /> Reset Current Chat

                        </span>

                    </button>
                    <a
                        href="https://www.google.com"
                        target='_blank'
                        rel='noreferrer'
                        className="w-full hover:text-gray-300 text-white font-bold block text-sm text-center"
                    >
                        LLM Usage Policy
                    </a>
                </div>
            </div>
        </div >
    );
};

export default Sidebar;
