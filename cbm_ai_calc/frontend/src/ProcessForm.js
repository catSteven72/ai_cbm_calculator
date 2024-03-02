import React, { useState } from 'react';
import './ProcessForm.css';

function getCsrfToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

function ProcessForm() {
    const [inputText, setInputText] = useState('');
    const [output, setOutput] = useState({ output_text: [], total_cbm: 0});
    const onlyDigits = (str) => /^\d*\.?\d*$/.test(str);
    const onlyIntegers = (str) => /^\d+$/.test(str);

    const handleEdit = (index, field, e) => {
        const currentValue = e.target.textContent;
        let isValidInput = false;

        if (field === 'NUM_PCS') {
            isValidInput = onlyIntegers(currentValue);
        } else {
            isValidInput = onlyDigits(currentValue);
        }

        if (isValidInput) {
            const parsedValue = field === 'NUM_PCS' ? parseInt(currentValue, 10) : parseFloat(currentValue);

            const updatedOutputText = output.output_text.map((item, itemIndex) => {
                if (index === itemIndex) {
                    const updatedItem = { ...item, [field]: parsedValue };
                    if ('length_meters' in updatedItem && 'width_meters' in updatedItem && 'height_meters' in updatedItem && 'NUM_PCS' in updatedItem) {
                        updatedItem.cbm = (updatedItem.length_meters * updatedItem.width_meters * updatedItem.height_meters) * updatedItem.NUM_PCS;
                    }
                    return updatedItem;
                }
                return item;
            });

            const updatedTotalCbm = updatedOutputText.reduce((total, item) => total + (item.cbm || 0), 0);

            setOutput({ ...output, output_text: updatedOutputText, total_cbm: updatedTotalCbm });
        }
        else {
            e.target.textContent = currentValue.slice(0, -1);
        }


    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const csrfToken = getCsrfToken();
        try {
            const response = await fetch('${process.env.REACT_APP_API_URL}', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ inputText })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setOutput(data);
        } catch (error) {
            console.error("There was an error:", error)
        }
    };

    return (
        <div className="container">
            <div className="input-section">
                <h2>Original input:</h2>
                <form onSubmit={handleSubmit}>
                    <textarea
                        className="process-form-textarea"
                        rows="10"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}>
                    </textarea>
                    <button className="process-form-button" type="submit">Process</button>
                </form>
            </div>
            {output && (
                <div className="output-section">
                    <h2>Output:</h2>
                    <div className="output-header">
                        <div>Number of Pieces</div>
                        <div>Length (m)</div>
                        <div>Width (m)</div>
                        <div>Height (m)</div>
                        <div>Cubic Meters (cbm)</div>
                    </div>
                    <div className="output-content">
                        {output.output_text.map((item, index) => (
                            <div key={index} className="output-row">
                                <div contentEditable={true} onBlur={(e) => handleEdit(index, 'NUM_PCS', e)}>
                                    {item.NUM_PCS}
                                </div>
                                <div contentEditable={true} onBlur={(e) => handleEdit(index, 'length_meters', e)}>
                                    {item.length_meters}
                                </div>
                                <div contentEditable={true} onBlur={(e) => handleEdit(index, 'width_meters', e)}>
                                    {item.width_meters}
                                </div>
                                <div contentEditable={true} onBlur={(e) => handleEdit(index, 'height_meters', e)}>
                                    {item.height_meters}
                                </div>
                                <div>
                                    {item.cbm.toFixed(3)}
                                </div>
                            </div>
                        ))}
                    </div>
                    <p>Total: {output.total_cbm.toFixed(3)} cbm</p>
                </div>
            )}
        </div>
    );
}

export default ProcessForm;