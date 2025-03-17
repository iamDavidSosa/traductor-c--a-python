import re
from tkinter import Tk, Text, Button, Label, Frame, END, Scrollbar, VERTICAL, RIGHT, Y, messagebox

# Análisis Léxico
def lexico(entrada):
    tokens = []
    lineas = entrada.split('\n')
    for num_linea, linea in enumerate(lineas, start=1):
        # Ignorar comentarios de una línea (//)
        linea = re.sub(r'//.*', '', linea)
        # Ignorar comentarios de múltiples líneas (/* ... */)
        if '/*' in linea:
            linea = re.sub(r'/\*.*?\*/', '', linea, flags=re.DOTALL)
        palabras = re.findall(r'\b\w+\b|[\+\-\*/%=(){},;]|".*?"', linea)
        for palabra in palabras:
            if re.match(r'\b(int|double|string|bool|if|else|for|while|try|catch|finally)\b', palabra):
                tokens.append(('PALABRA_CLAVE', palabra, num_linea))
            elif re.match(r'\b(true|false)\b', palabra):
                tokens.append(('VALOR_BOOL', palabra, num_linea))
            elif re.match(r'\b\d+\b', palabra):
                tokens.append(('NUMERO', palabra, num_linea))
            elif re.match(r'\b\w+\b', palabra):
                tokens.append(('IDENTIFICADOR', palabra, num_linea))
            elif re.match(r'[\+\-\*/%=]', palabra):
                tokens.append(('OPERADOR', palabra, num_linea))
            elif re.match(r'[{}();,]', palabra):
                tokens.append(('SIMBOLO', palabra, num_linea))
            elif re.match(r'^".*"$', palabra):
                tokens.append(('TEXTO', palabra, num_linea))
            else:
                tokens.append(('DESCONOCIDO', palabra, num_linea))
    return tokens

# Análisis Sintáctico
def sintactico(tokens):
    stack = []
    for token in tokens:
        if token[1] == '{':
            stack.append(('{', token[2]))  # Guardar la línea de la llave abierta
        elif token[1] == '}':
            if not stack:
                return False, f"Error de sintaxis: Llave de cierre '}}' sin llave de apertura en línea {token[2]}"
            if stack[-1][0] == '{':
                stack.pop()
            else:
                return False, f"Error de sintaxis: Llave de cierre '}}' no coincide con llave de apertura en línea {token[2]}"
    if stack:
        return False, f"Error de sintaxis: Llave de apertura '{{' sin cierre en línea {stack[-1][1]}"
    return True, ""

# Análisis Semántico
def semantico(tokens):
    variables = {}  # Diccionario para guardar el tipo de cada variable
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token[0] == 'PALABRA_CLAVE' and token[1] in ['int', 'double', 'string', 'bool']:
            tipo = token[1]
            if i + 1 < len(tokens) and tokens[i + 1][0] == 'IDENTIFICADOR':
                nombre_var = tokens[i + 1][1]
                if i + 2 < len(tokens) and tokens[i + 2][1] == '=':
                    # Verificar el valor asignado
                    valor = tokens[i + 3][1] if i + 3 < len(tokens) else None
                    if tipo == 'int':
                        if not (valor and re.match(r'^\d+$', valor)):
                            return False, f"Error semántico: Se esperaba un valor entero para '{nombre_var}' en línea {token[2]}"
                    elif tipo == 'double':
                        if not (valor and re.match(r'^\d*\.?\d+$', valor)):
                            return False, f"Error semántico: Se esperaba un valor double para '{nombre_var}' en línea {token[2]}"
                    elif tipo == 'string':
                        if not (valor and valor.startswith('"') and valor.endswith('"')):
                            return False, f"Error semántico: Se esperaba una cadena para '{nombre_var}' en línea {token[2]}"
                    elif tipo == 'bool':
                        if not (valor and valor in ['true', 'false']):
                            return False, f"Error semántico: Se esperaba un valor booleano (true/false) para '{nombre_var}' en línea {token[2]}"
                variables[nombre_var] = tipo
                i += 2  # Saltar el tipo y el identificador
            else:
                i += 1
        elif token[0] == 'IDENTIFICADOR':
            # Si es un identificador, verificar si está declarado
            if token[1] not in variables and token[1] != 'Console' and token[1] != 'WriteLine':
                return False, f"Error semántico: Variable '{token[1]}' no declarada en línea {token[2]}"
            i += 1
        else:
            i += 1
    return True, ""

def traducir_a_python(entrada):
    lineas = entrada.split('\n')
    python_code = []
    for linea in lineas:
        # Ignorar comentarios de una línea (//)
        linea = re.sub(r'//.*', '', linea)
        # Ignorar comentarios de múltiples líneas (/* ... */)
        if '/*' in linea:
            linea = re.sub(r'/\*.*?\*/', '', linea, flags=re.DOTALL)
        linea = linea.strip()
        if not linea:
            continue
        if 'Console.WriteLine' in linea:
            # Extraer el contenido dentro de los paréntesis
            contenido = linea.split('(', 1)[1].rsplit(')', 1)[0].strip()
            if contenido.startswith('"') and contenido.endswith('"'):
                # Si es un texto entre comillas
                texto = contenido[1:-1]
                python_code.append(f'print("{texto}")')
            else:
                # Si es una variable o expresión
                python_code.append(f'print({contenido})')
        elif 'int ' in linea or 'double ' in linea or 'string ' in linea or 'bool ' in linea:
            partes = linea.split()
            nombre_var = partes[1].replace(';', '')
            valor = 'None'
            if '=' in linea:
                valor = linea.split('=')[1].replace(';', '').strip()
            python_code.append(f'{nombre_var} = {valor}')
        elif 'if (' in linea:
            condicion = linea.split('(')[1].split(')')[0]
            python_code.append(f'if {condicion}:')
        elif 'else if (' in linea:
            condicion = linea.split('(')[1].split(')')[0]
            python_code.append(f'elif {condicion}:')
        elif 'else' in linea:
            python_code.append('else:')
        elif 'for (' in linea:
            # Extraer las partes del bucle for
            partes = linea.split(';')
            inicio = partes[0].split('(')[1].strip()
            condicion = partes[1].strip()
            incremento = partes[2].split(')')[0].strip()
            # Convertir a sintaxis de Python
            if 'int ' in inicio:
                inicio = inicio.replace('int ', '')
            if '++' in incremento:
                incremento = incremento.replace('++', '+= 1')
            python_code.append(f'for {inicio}; {condicion}; {incremento}:')
        elif 'while (' in linea:
            condicion = linea.split('(')[1].split(')')[0]
            python_code.append(f'while {condicion}:')
        elif 'do {' in linea:
            python_code.append('while True:')
        elif 'switch (' in linea:
            variable = linea.split('(')[1].split(')')[0]
            python_code.append(f'switch_{variable}:')
        elif 'case ' in linea:
            valor = linea.split()[1].replace(':', '').strip()
            python_code.append(f'if {variable} == {valor}:')
        elif 'default:' in linea:
            python_code.append('else:')
        elif 'break;' in linea:
            python_code.append('break')
        elif 'try {' in linea:
            python_code.append('try:')
        elif 'catch (' in linea:
            python_code.append('except:')
        elif 'finally {' in linea:
            python_code.append('finally:')
        elif '}' in linea:
            python_code.append('')
        else:
            python_code.append(linea)
    return '\n'.join(python_code)

# Interfaz Gráfica
def traducir():
    entrada = texto_entrada.get("1.0", END).strip()
    tokens = lexico(entrada)
    
    # Verificación sintáctica
    sintaxis_valida, mensaje_sintaxis = sintactico(tokens)
    if not sintaxis_valida:
        texto_salida.delete("1.0", END)
        texto_salida.insert("1.0", f"Error de sintaxis:\n{mensaje_sintaxis}")
        return
    
    # Verificación semántica
    semantica_valida, mensaje_semantica = semantico(tokens)
    if not semantica_valida:
        texto_salida.delete("1.0", END)
        texto_salida.insert("1.0", f"Error semántico:\n{mensaje_semantica}")
        return
    
    # Traducción a Python
    codigo_python = traducir_a_python(entrada)
    texto_salida.delete("1.0", END)
    texto_salida.insert("1.0", f"Código Python:\n{codigo_python}")

# Configuración de la ventana
root = Tk()
root.title("Traductor de C# a Python")

frame = Frame(root)
frame.pack(pady=10)

label_entrada = Label(frame, text="Código C#:")
label_entrada.grid(row=0, column=0)

texto_entrada = Text(frame, width=60, height=20)
texto_entrada.grid(row=1, column=0)

scroll_entrada = Scrollbar(frame, orient=VERTICAL, command=texto_entrada.yview)
scroll_entrada.grid(row=1, column=1, sticky='ns')
texto_entrada.config(yscrollcommand=scroll_entrada.set)

label_salida = Label(frame, text="Código Python:")
label_salida.grid(row=0, column=2)

texto_salida = Text(frame, width=60, height=20)
texto_salida.grid(row=1, column=2)

scroll_salida = Scrollbar(frame, orient=VERTICAL, command=texto_salida.yview)
scroll_salida.grid(row=1, column=3, sticky='ns')
texto_salida.config(yscrollcommand=scroll_salida.set)

boton_traducir = Button(frame, text="Traducir", command=traducir)
boton_traducir.grid(row=2, column=0, columnspan=4)

root.mainloop()