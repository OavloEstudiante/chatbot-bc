import http.server
import json
import re
import os
import socketserver
import unicodedata

PUERTO = int(os.environ.get("PORT", 8080))

def normalizar_texto(texto: str) -> str:
    """Elimina tildes, caracteres especiales y unifica espacios en minusculas."""
    texto_sin_acento = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto_limpio = re.sub(r'[^a-zA-Z0-9\s]', ' ', texto_sin_acento)
    return ' '.join(texto_limpio.lower().split())

def responder_consulta(entrada_usuario: str) -> str:
    consulta = normalizar_texto(entrada_usuario)
    
    if not consulta:
        return "Por favor, escribe tu consulta sobre el trámite del Sistema Auxiliar de Pagos."

    # Regla 1: Detección y advertencia inmediata de datos personales (Filtro LOPD)
    patron_correo = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    patron_telefono = r'\b(\+?593|0)?[ -]?[9]\d{8}\b'
    patron_cedula = r'\b\d{10}\b'
    
    if (re.search(patron_correo, entrada_usuario) or 
        re.search(patron_telefono, entrada_usuario) or 
        re.search(patron_cedula, entrada_usuario)):
        return (
            "[Aviso de Privacidad] Recuerda que por seguridad no debes ingresar datos personales "
            "(cédula, correos o teléfonos) por este canal. El asistente nunca almacena ni solicita tu información."
        )

    # Regla 2: Intentos de solicitar plantillas, modelos o certificados de firma digital (Pregunta Tramposa)
    terminos_tramposos = [
        "modelo de firma", "plantilla de firma", "ejemplo de firma", "descargar firma", 
        "archivo de firma", "formato de firma", "token de firma", "donde compro firma", 
        "firma electronica de muestra", "modelo firma", "machote de firma", "certificado digital", 
        "prestar firma", "dame una firma", "modelo de certificado", "ejemplo firma", 
        "formato firma digital"
    ]
    if any(k in consulta for k in terminos_tramposos):
        return "Lo siento, no puedo proporcionar ese documento. Por favor, utilice su firma electrónica habitual o consulte a su área de TI."

    # Regla 3: Dudas sobre aprobación, tiempos, estados o promesas de acceso (Pregunta Rechazo)
    terminos_aprobacion = [
        "cuando aprueban", "cuando me aprueban", "fecha de aprobacion", "cuanto tardan en aprobar", 
        "ya esta aprobado", "van a aprobar", "tiempo de demora", "cuanto demora", "cuanto se tarda", 
        "plazo de calificacion", "estado de mi tramite", "revisar aprobacion", "me van a aceptar", 
        "cuando me aceptan", "cuando responden", "cuantos dias demora", "cuanto tiempo toma", 
        "garantizan aprobacion", "estoy calificado", "puedes verificar si me aprobaron"
    ]
    if any(k in consulta for k in terminos_aprobacion):
        return "No puedo predecir la aprobación. El BCE enviará la respuesta al correo indicado en su solicitud."

    # Regla 4: Consultas complejas, soporte humano o quejas fuera de alcance (Derivación)
    terminos_soporte = [
        "humano", "asesor", "agente", "reclamo", "demanda", "queja", "persona", 
        "operador", "alguien real", "atencion al cliente", "funcionario", "ejecutivo", 
        "denuncia", "problema legal", "hablar con alguien", "soporte bce"
    ]
    if any(k in consulta for k in terminos_soporte):
        return "Voy a derivarte a un agente del BCE."

    # Regla 5: Cómo redactar, firmar y enviar la solicitud oficial (Pregunta Normal)
    terminos_solicitud = [
        "como solicito", "requerimiento escrito", "pasos solicitud", "como hacer la solicitud", 
        "redactar solicitud", "carta de solicitud", "redaccion de carta", "mandar requerimiento", 
        "que debe decir la solicitud", "meter papeles", "mandar solicitud", "iniciar tramite", 
        "postular", "como me califico", "proceso de calificacion", "oficio al bce", "como envio la carta", 
        "formato de oficio", "que datos debe llevar la carta", "solicitud escrita", "requerimiento formal"
    ]
    if any(k in consulta for k in terminos_solicitud):
        return (
            "Para realizar la solicitud oficial, sigue estos sencillos pasos:<br>"
            "1. Redacta una carta de solicitud formal con el requerimiento de calificación.<br>"
            "2. Incluye obligatoriamente: correo electrónico de contacto, número de celular y datos oficiales de la institución.<br>"
            "3. Aplica tu firma electrónica válida al documento.<br>"
            "4. Remite la solicitud debidamente firmada al Banco Central del Ecuador a través de sus canales oficiales de recepción."
        )

    # Regla 6: Notificación, recepción de respuesta y entrega de guía
    terminos_notificacion = [
        "respuesta", "notificacion", "guia explicativa", "guia", "donde responden", 
        "como me avisan", "como me entero", "por donde me llega", "a donde mandan la respuesta", 
        "donde me llega la guia", "correo de respuesta", "manual explicativo", "documento explicativo", 
        "notificacion oficial", "aviso del bce"
    ]
    if any(k in consulta for k in terminos_notificacion):
        return (
            "Una vez revisada la información, el Banco Central del Ecuador enviará la respuesta oficial "
            "al correo electrónico que indicaste en la solicitud, adjuntando la guía explicativa con los pasos detallados."
        )

    # Regla 7: Carga de información diaria, monitoreo y reportes
    terminos_carga = [
        "informacion diaria", "subir informacion", "cargar informacion", "monitoreo", "como subo", 
        "subir datos", "cargar reportes", "planillas diarias", "reporte diario", "donde cargo los datos", 
        "plataforma de carga", "subir archivos", "subir documentos diarios", "control diario", 
        "subir la informacion diaria", "monitoreo diario"
    ]
    if any(k in consulta for k in terminos_carga):
        return (
            "La carga de información diaria corresponde al monitoreo que el BCE aplica a todos los usuarios. "
            "Los pasos específicos para cargar estos reportes se encuentran detallados en la guía explicativa "
            "que recibirás por correo una vez revisada tu solicitud."
        )

    # Regla 8: Requisitos y funcionamiento general
    terminos_requisitos = [
        "requisitos", "que necesito", "que pide", "pasos", "como funciona", 
        "documentacion", "que documentos piden", "que debo tener", "condiciones", 
        "que se necesita", "requisitos obligatorios", "documentos necesarios"
    ]
    if any(k in consulta for k in terminos_requisitos):
        return (
            "El trámite requiere presentar una solicitud escrita con firma electrónica que contenga el correo, "
            "celular y datos de tu institución. Tras la revisión, el BCE te notificará por correo y enviará la "
            "guía explicativa para la carga de información diaria de monitoreo."
        )

    # Regla 9: Saludos y despedidas
    terminos_saludos = [
        "hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", 
        "saludos", "estimados", "que tal", "que mas"
    ]
    if any(k in consulta for k in terminos_saludos):
        return (
            "¡Hola! Soy el asistente virtual del Banco Central del Ecuador (BCE). "
            "Te puedo orientar con los pasos para calificarte y subir la información diaria en el Sistema Auxiliar de Pagos. ¿En qué te puedo ayudar hoy?"
        )
        
    terminos_despedida = [
        "gracias", "adios", "chao", "hasta luego", "muchas gracias", "muy amable", "nos vemos"
    ]
    if any(k in consulta for k in terminos_despedida):
        return "¡Hasta luego! Recuerda que el BCE está para servirte. Que tengas un buen día."

    # Respuesta predeterminada
    return "No dispongo de información suficiente para esa consulta puntual. Si requieres asistencia técnica o detallada, voy a derivarte a un agente del BCE."

HTML_PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Asistente Ciudadano - Banco Central del Ecuador</title>
  <style>
    * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: #f0f2f5; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .chat-container { width: 100%; max-width: 680px; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; height: 88vh; }
    .chat-header { background: #003366; color: white; padding: 16px 20px; }
    .chat-header h1 { margin: 0; font-size: 1.15rem; font-weight: 700; }
    .chat-header p { margin: 4px 0 0; font-size: 0.8rem; opacity: 0.85; }
    .messages-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
    .message { max-width: 82%; padding: 12px 16px; border-radius: 12px; font-size: 0.92rem; line-height: 1.45; word-wrap: break-word; }
    .bot-msg { background: #e9ecef; color: #212529; align-self: flex-start; border-bottom-left-radius: 2px; }
    .user-msg { background: #003366; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
    
    /* Panel de Sugerencias */
    .suggestions-container { padding: 10px 16px; background: #f8f9fa; border-top: 1px solid #e9ecef; }
    .suggestions-title { font-size: 0.75rem; font-weight: 600; color: #6c757d; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
    .suggestions-list { display: flex; flex-wrap: wrap; gap: 6px; }
    .sugg-btn { background: #ffffff; border: 1px solid #ced4da; color: #003366; border-radius: 16px; padding: 6px 12px; font-size: 0.78rem; cursor: pointer; transition: all 0.2s ease; font-weight: 500; }
    .sugg-btn:hover { background: #003366; color: #ffffff; border-color: #003366; }

    .input-box { display: flex; padding: 12px 16px; border-top: 1px solid #dee2e6; background: #ffffff; gap: 10px; }
    input[type="text"] { flex: 1; padding: 12px 18px; border: 1px solid #ced4da; border-radius: 25px; outline: none; font-size: 0.92rem; }
    input[type="text"]:focus { border-color: #003366; }
    button.send-btn { background: #003366; color: white; border: none; padding: 10px 22px; border-radius: 25px; cursor: pointer; font-weight: 600; font-size: 0.92rem; }
    button.send-btn:hover { background: #002244; }
  </style>
</head>
<body>
  <div class="chat-container">
    <div class="chat-header">
      <h1>Banco Central del Ecuador</h1>
      <p>Asistente Ciudadano: Trámite Sistema Auxiliar de Pagos</p>
    </div>
    
    <div class="messages-box" id="chat">
      <div class="message bot-msg">
        ¡Hola! Soy el asistente virtual del Banco Central del Ecuador (BCE). Puedo orientarte sobre los requisitos y pasos para calificarte y subir información diaria en el Sistema Auxiliar de Pagos.
      </div>
    </div>

    <!-- Preguntas Rápidas Sugeridas -->
    <div class="suggestions-container">
      <div class="suggestions-title">Preguntas sugeridas:</div>
      <div class="suggestions-list">
        <button class="sugg-btn" onclick="enviarSugerida('¿Cómo solicito el requerimiento escrito con firma electrónica?')">¿Cómo hago la solicitud?</button>
        <button class="sugg-btn" onclick="enviarSugerida('¿Qué requisitos necesito para calificarme?')">Requisitos obligatorios</button>
        <button class="sugg-btn" onclick="enviarSugerida('¿Cuándo me aprobarán el acceso al Sistema Auxiliar de Pagos?')">¿Cuándo me aprueban?</button>
        <button class="sugg-btn" onclick="enviarSugerida('¿Me puedes enviar un modelo de firma electrónica para que lo use en la solicitud?')">Modelo de firma electrónica</button>
        <button class="sugg-btn" onclick="enviarSugerida('¿Cómo subo la información diaria de monitoreo?')">Información diaria</button>
      </div>
    </div>

    <form class="input-box" onsubmit="enviar(event)">
      <input type="text" id="mensaje" placeholder="Escribe tu consulta aquí..." autocomplete="off" />
      <button type="submit" class="send-btn">Enviar</button>
    </form>
  </div>

  <script>
    async function enviarTexto(texto) {
      if (!texto) return;
      const chat = document.getElementById('chat');
      chat.innerHTML += `<div class="message user-msg">${texto}</div>`;
      chat.scrollTop = chat.scrollHeight;

      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mensaje: texto })
        });
        const data = await res.json();
        chat.innerHTML += `<div class="message bot-msg">${data.respuesta}</div>`;
      } catch (err) {
        chat.innerHTML += `<div class="message bot-msg">Error de conexión con el servidor.</div>`;
      }
      chat.scrollTop = chat.scrollHeight;
    }

    function enviar(e) {
      e.preventDefault();
      const input = document.getElementById('mensaje');
      const texto = input.value.trim();
      if (!texto) return;
      input.value = '';
      enviarTexto(texto);
    }

    function enviarSugerida(pregunta) {
      enviarTexto(pregunta);
    }
  </script>
</body>
</html>
"""

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGINA.encode('utf-8'))

    def do_POST(self):
        if self.path == "/chat":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            datos = json.loads(body.decode('utf-8'))
            pregunta = datos.get("mensaje", "")
            
            respuesta = responder_consulta(pregunta)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"respuesta": respuesta}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silencia los logs de peticiones HTTP en la consola

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PUERTO), ChatHandler) as httpd:
        print("=" * 60)
        print("  Servidor Web Activo del Asistente BCE")
        print(f"  Abre este enlace en Chrome: http://localhost:{PUERTO}")
        print("  (Presiona Ctrl + C en esta terminal para detenerlo)")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")