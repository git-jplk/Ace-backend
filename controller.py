import json
import os
import re
import unicodedata
from flask import Flask, request, jsonify
from model import QueryService
from werkzeug.utils import secure_filename
from flow import invoke_flow
app = Flask(__name__)
query_service = QueryService()
def clean_text(text: str) -> str:
    # Normalize unicode (e.g. turn “ﬁ” ligature into “fi”)
    text = unicodedata.normalize('NFKC', text)
    # Remove any non-printable/control chars
    text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
    # Collapse all whitespace (newlines, tabs, multiple spaces) into single spaces
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()



@app.route('/start-search', methods=['POST'])
async def start_search():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required in the request body.'}), 400

    content = data['content']
    try:
        result = await invoke_flow(content)
        #result = {"result":{"justifications":{"market_score":"The market size is described as the 'Global startup ecosystem', which is vast and growing, but lacks specific quantitative data to fully assess the market potential.","overall_score":"The overall score reflects a solid team and innovative product but is tempered by unknowns in market traction and competition.","product_score":"The pitch emphasizes innovative connections to Silicon Valley resources, supported by a high innovation score of 8, indicating a strong product offering.","risk_score":"The risk is moderate due to the competitive landscape of startup incubation platforms, along with the absence of detailed traction metrics.","team_score":"The founder, Roger Rappoport, has relevant experience as a corporate attorney and angel investor, indicating a strong understanding of the startup landscape. However, limited information on the rest of the team affects the score.","traction_score":"There is no data provided on revenue, user growth, or partnerships, which results in a lower score for traction despite the potential indicated by the business model."},"market_score":7,"overall_score":6.8,"product_score":8,"risk_score":6,"summary":"Access Silicon Valley presents a promising concept aimed at connecting entrepreneurs with valuable resources in the startup ecosystem. The founder's experience and the innovative nature of the product are strong points. However, the lack of traction data and competition details raises concerns about market positioning and sustainability. Overall, while there is potential, careful monitoring of competition and revenue generation will be crucial for success.","team_score":8,"traction_score":5}}
        return jsonify({'result':result}), 200
    except Exception as e:
        print(f"Error during query: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
async def get_company():
    data = request.get_json()
    if not data or 'context' not in data or 'message' not in data:
        return jsonify({'error': 'Both "context" and "message" are required in the request body.'}), 400

    context = data['context']
    message = data['message']
    if isinstance(context, dict):
        context = json.dumps(context)
    
    context = "Answer the following question based on the context provided of evaluation of a startup company: " + context + "  This is the question by the user: " + message
    try:
        result = query_service.query_raw(context, additional_info= " ")
        print(result)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
