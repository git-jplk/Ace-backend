from flask import Flask, request, jsonify
from model import QueryService
app = Flask(__name__)
query_service = QueryService()

@app.route('/evaluate', methods=['GET'])
async def get_company():
    company_name = request.args.get('name')
    if not company_name:
        return jsonify({'error': 'Company name is required'}), 400
    try:
        result = await query_service.query(company_name)
        print(result)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
