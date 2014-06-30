function Torneo(){
    this.nombre = 'Brasil 2014';
    this.partidos = [];
    this.participantes = [];
}
Torneo.prototype.apuestasPara = function(unPartido){
    var totParticipantes = this.participantes.length;
    var apuestas = [];
    for(var i=0; i < totParticipantes; i++){
        apuestas.push(this.participantes[i].apuestaPara(unPartido));
    }
    return apuestas;
}

Torneo.prototype.agregarPartido = function(p){
    p.torneo = this;
    this.partidos.push(p)
}
Torneo.prototype.partidos = function(){
    return this.partidos;
}

function Equipo(codigo){
}

function Partido(id, datos){
    this.id = id;
    this.datos = datos;
}
Partido.prototype.cantApuestasPor = function(resultado){
    var apuestas = this.torneo.apuestasPara(this);
    var totApuestas = apuestas.length;
    var totApuestasPor=0;
    for(var i=0; i<totApuestas; i++){
        if(apuestas[0].resultado() == resultado){
            totApuestasPor++;
        }
    }
    return totApuestasPor;
}
Partido.prototype.resultado = function(){
    return (this.datos.gl > this.datos.gv)? 'L' : ((this.datos.gl < this.datos.gv)? 'V' : 'E');
}

function Participante(id, nombre, apuestas){
}