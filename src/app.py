from flask import Flask
from flask import render_template, request, redirect
from flaskext.mysql import MySQL

app= Flask(__name__)
mysql= MySQL()

app.config['MYSQL_DATABASE_HOST']= 'localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']= 'root'
app.config['MYSQL_DATABASE_DB']= 'empleados'
mysql.init_app(app)


@app.route('/') # define una ruta de acceso
def index():
    conn=mysql.connect()
    cursor = conn.cursor()

    sql= "SELECT * FROM `empleados`.`empleados`;"
    cursor.execute(sql)
    
    empleados = cursor.fetchall()

    conn.commit()

    return render_template('empleados/index.html', empleados=empleados)

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre'] # lo recibe del form
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto'] # lo recibe como archivo, un stream de datos
    
    sql= "INSERT INTO  `empleados`.`empleados` (nombre, correo, foto) VALUES (%s,%s,%s);"
    datos= (_nombre,_correo,_foto.filename)

    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)

    conn.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)