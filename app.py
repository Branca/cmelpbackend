# ========================================
# ARQUIVO 1: app.py (COM GROQ - GRÁTIS)
# ========================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Logging inicial
print("=" * 50, file=sys.stderr)
print("CMELP Backend Starting...", file=sys.stderr)
print(f"PORT: {os.environ.get('PORT', 'NOT SET')}", file=sys.stderr)
print(f"GROQ_API_KEY: {'SET ✓' if os.environ.get('GROQ_API_KEY') else 'NOT SET ✗'}", file=sys.stderr)
print("=" * 50, file=sys.stderr)

app = Flask(__name__)
CORS(app)

# Inicializar Groq com tratamento de erro
try:
    from groq import Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    print("✓ Groq client initialized successfully", file=sys.stderr)
except Exception as e:
    print(f"✗ Error initializing Groq: {e}", file=sys.stderr)
    client = None

# Base de conhecimento CMELP
CMELP_KNOWLEDGE = """
SOBRE A CMELP:
A CMELP (Central de Mídia para o Ensino da Língua Portuguesa) é uma plataforma 
online de ensino de português brasileiro.

MÓDULO 4 - NÍVEL A2.2 (Conteúdo do curso):

LIÇÃO 1: Poderia avisá-lo, por favor?
- Pronomes Oblíquos (me, te, o, a, lhe, nos, vos, se)
- Formas especiais: lo/la (após r/s/z), no/na (após nasal)
- Sons do C, S, SC: diferentes pronúncias
- Vocabulário: Partes do carro (volante, câmbio, faróis, etc)
- Problemas com veículos e multas de trânsito

LIÇÃO 2: As mais belas praias do mundo
- Comparativos: mais/menos... que/do que
- Superlativos: o mais... de, -íssimo
- Monotongação (mudança de ditongo para vogal simples)
- Conjunções: e, mas, ou, porque, portanto, então
- Praias brasileiras: Baía do Sancho, Praia dos Carneiros
- Esportes aquáticos e ao ar livre

LIÇÃO 3: Siga em frente!
- Imperativo afirmativo e negativo
- Dar ordens, instruções, conselhos
- Pontuação: ponto, vírgula, ponto de exclamação, interrogação
- Acentuação tônica
- Ditongação (criar ditongo na fala)
- Feng Shui e decoração de ambientes

LIÇÃO 4: Tomara que todos me entendam!
- Presente do Subjuntivo (expressa dúvida, desejo, ordem)
- Formação: verbos -AR → E, verbos -ER/-IR → A
- Expressões impessoais: É bom que, É provável que, É importante que
- Sons do X: cinco sons diferentes (ch, z, s, ks, ss)
- Pronomes indefinidos: alguém, ninguém, algo, nada
- Diversidade linguística e sotaques

LIÇÃO 5: O profissional do futuro
- Estrangeirismos: palavras de outros idiomas no português
- Falsos amigos/cognatos: palavras parecidas com significados diferentes
- Revisão de Pronomes Oblíquos
- Mercado de trabalho e profissões do futuro
- Competências profissionais

DICAS DE ENSINO:
- Sempre dê exemplos práticos
- Use contexto da lição atual quando possível
- Seja paciente e encorajador
- Corrija erros gentilmente
- Incentive a prática
"""

SYSTEM_PROMPT = f"""Você é o assistente virtual da CMELP, especializado em ensino de língua portuguesa.

{CMELP_KNOWLEDGE}

SUAS RESPONSABILIDADES:
1. Explicar gramática de forma clara e didática
2. Ajudar com exercícios do curso
3. Esclarecer dúvidas sobre a plataforma
4. Dar exemplos práticos e contextualizados
5. Corrigir erros gentilmente

DIRETRIZES:
- Sempre seja educado, paciente e didático
- Use português brasileiro
- Dê exemplos concretos ao explicar conceitos
- Se não souber algo específico da plataforma, seja honesto
- Incentive o aluno a continuar estudando
- Respostas claras mas completas (não muito longas)
- Use emojis ocasionalmente para tornar mais amigável
"""

# Histórico de conversas (em memória)
conversations = {}

@app.route('/')
def home():
    print(">>> Route / accessed", file=sys.stderr)
    return jsonify({
        'status': 'online',
        'service': 'CMELP AI Assistant',
        'version': '1.0',
        'model': 'Mixtral-8x7b (Groq)',
        'cost': 'FREE!'
    })

@app.route('/health')
def health():
    print(">>> Route /health accessed", file=sys.stderr)
    return jsonify({'status': 'healthy'})

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    print(">>> Route /chat accessed", file=sys.stderr)
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    # Verificar se Groq está disponível
    if client is None:
        print("✗ Groq client not available", file=sys.stderr)
        return jsonify({
            'error': 'Groq client not initialized. Check GROQ_API_KEY.'
        }), 500
    
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        context = data.get('context', {})
        
        print(f"User message: {user_message[:50]}...", file=sys.stderr)
        
        if not user_message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Inicializar histórico se não existir
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Adicionar contexto da página se disponível
        if context.get('page'):
            user_message = f"[Contexto: Aluno está em '{context['page']}'] {user_message}"
        
        # Adicionar mensagem do usuário
        conversations[session_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Preparar mensagens com system prompt
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + conversations[session_id]
        
        print("Calling Groq API...", file=sys.stderr)
        
        # Chamar Groq API (GRATUITA!)
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Excelente modelo, grátis!
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
            top_p=1,
            stream=False
        )
        
        # Extrair resposta
        assistant_message = completion.choices[0].message.content
        
        print(f"Response received: {len(assistant_message)} chars", file=sys.stderr)
        
        # Adicionar ao histórico
        conversations[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Limitar histórico (últimas 10 mensagens)
        if len(conversations[session_id]) > 10:
            conversations[session_id] = conversations[session_id][-10:]
        
        return jsonify({
            'response': assistant_message,
            'session_id': session_id
        })
    
    except Exception as e:
        print(f"✗ Error in /chat: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            'error': 'Erro ao processar mensagem',
            'details': str(e)
        }), 500

@app.route('/clear-history', methods=['POST'])
def clear_history():
    print(">>> Route /clear-history accessed", file=sys.stderr)
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversations:
        conversations[session_id] = []
    
    return jsonify({'message': 'Histórico limpo com sucesso'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask on port {port}...", file=sys.stderr)
    app.run(host='0.0.0.0', port=port, debug=False)
