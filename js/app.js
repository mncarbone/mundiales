Class = window;

Class.Torneo = 

	function(datosParticipantes, datosPartidos){
		this.nombre = 'Brasil 2014';
		this.datosParticipantes = '';
		this.datosPartidos = '';
		this.partidos = {};
		this.participantes = {};
		this.participantesOrdenados = [];
		this.actualizar(datosParticipantes, datosPartidos);
	}; def = Torneo.prototype;

	def.actualizar = function(datosParticipantes, datosPartidos){
		var actualizaParticipantes = this.cargarParticipantes(datosParticipantes);
		var actualizaPartidos = this.cargarPartidos(datosPartidos);
		return actualizaParticipantes || actualizaPartidos;
	}
	
	def.cargarParticipantes = function(datosParticipantes){
		if(this.datosParticipantes == JSON.stringify(datosParticipantes)){
			return false;
		}
		else {
			this.datosParticipantes = JSON.stringify(datosParticipantes);
			this.participantesOrdenados = [];
			var tot = datosParticipantes.length;
			for(var i=0; i < tot; i++){
				datos = datosParticipantes[i];
				var participante = new Participante(this, datos)
				this.participantes[participante.id] = participante;
				this.participantesOrdenados.push(participante);
			}
			return true;
		}
	}

	def.cargarPartidos = function(datosPartidos){
		if(this.datosPartidos == JSON.stringify(datosPartidos)){
			return false;
		}
		else {
			this.datosPartidos = JSON.stringify(datosPartidos);
			var tot = datosPartidos.length;
			for(var i=0; i < tot; i++){
				datos = datosPartidos[i];
				var partido = new Partido(this, datos);
				this.partidos[partido.id] = partido;
			}
			return true;
		}
	}
	
	def.cantApuestasPara = function(unPartido,unResultado){
		var cant = 0;
		var tot = this.participantesOrdenados.length
		for(var i = 0; i < tot; i++){
			var participante = this.participantesOrdenados[i];
            var apuesta = participante.apuestaPara(unPartido)
			if(apuesta && apuesta.resultado == unResultado){
                cant++;
            }
		}
		return cant;
	}

	
	def.getPartido = function(id){
		return this.partidos[id];
	}
	
	def.getPartidos = function(){
		return this.partidos;
	}
	
	def.getParticipante = function(id){
		return this.participantes[id];
	}
	
	def.getParticipantes = function(){	
		this.participantesOrdenados.sort(function(a, b) {
			var pa = a.getPuntos()
			var pb = b.getPuntos()
			return (pa == pb)? (a.nombre.toUpperCase().localeCompare(b.nombre.toUpperCase())) : (pb - pa);
		});
		return this.participantesOrdenados;
	}


Class.Equipo = 

	function(codigo){
		this.codigo = (codigo != 'TBD')? codigo : '???';;
		this.bandea = this.getBandera();
	}; def = Equipo.prototype;
	
	def.getBandera = function (){
			var codes = {};
			codes['ALG'] = 'dz';
			codes['ARG'] = 'ar';
			codes['AUS'] = 'au';
			codes['BEL'] = 'be';
			codes['BIH'] = 'ba';
			codes['BRA'] = 'br';
			codes['CHI'] = 'cl';
			codes['CIV'] = 'ci';
			codes['CMR'] = 'cm';
			codes['COL'] = 'co';
			codes['CRC'] = 'cr';
			codes['CRO'] = 'hr';
			codes['ECU'] = 'ec';
			codes['ENG'] = 'england';
			codes['ESP'] = 'es';
			codes['FRA'] = 'fr';
			codes['GER'] = 'de';
			codes['GHA'] = 'gh';
			codes['GRE'] = 'gr';
			codes['HON'] = 'hn';
			codes['IRN'] = 'ir';
			codes['ITA'] = 'it';
			codes['JPN'] = 'jp';
			codes['KOR'] = 'kr';
			codes['MEX'] = 'mx';
			codes['NED'] = 'nl';
			codes['NGA'] = 'ng';
			codes['POR'] = 'pt';
			codes['RUS'] = 'ru';
			codes['SUI'] = 'ch';
			codes['URU'] = 'uy';
			codes['USA'] = 'us';
			return codes[this.codigo];
	}

Class.Partido = 
	
	function(torneo, datos){

			
		this.torneo = torneo;
		this.id = datos.match_number;
		this.datos = datos;
		this.local = new Equipo(datos.home_team.code);
		this.visitante = new Equipo(datos.away_team.code);
		this.iniciado = (datos.status != 'future');
		this.golesLocal = (this.iniciado)? datos.home_team.goals : '-' ;
		this.golesVisitante = (this.iniciado)? datos.away_team.goals : '-';
		this.resultado = this.getResultado();

		var datetime = datos.datetime.split('T');
		this.dia = datetime[0];
		var horamin = datetime[1].split('.')[0].split(':');
		this.hora = horamin[0] + ':' + horamin[1];
		this.apuestasPor = {'L':'','E':'','V':''};
	}; def = Partido.prototype;
	
	def.cantApuestasPor = function(resultado){
        if(this.apuestasPor[resultado] == ''){
            this.apuestasPor[resultado] = this.torneo.cantApuestasPara(this,resultado); 
        }
		return this.apuestasPor[resultado];
	}
	
	def.getResultado = function(){
		return (this.iniciado)? (
			(this.golesLocal > this.golesVisitante)? 'L' : (
			(this.golesLocal < this.golesVisitante)? 'V' : 'E')
		) : '-';
	}

	
Class.Participante = 

	function (torneo, datos){
		this.torneo = torneo;
		this.id = datos.id;
		this.nombre = datos.nombre;
		this.apuestas = {};
		this.cargarApuestas(datos.apuestas);
		this.puntos = '';
	}; def = Participante.prototype;
	
	def.cargarApuestas = function(apuestas){
		var tot = apuestas.length;
		for(var i=0; i<tot; i++){
			var datos = apuestas[i];
			var apuesta = new Apuesta(this.torneo, datos);
			this.apuestas[datos.id] = apuesta;
		}
	}
	
	def.apuestaPara = function(unPartido){
        if(this.apuestas.hasOwnProperty(unPartido.id)){
            return this.apuestas[unPartido.id];
        }
        else{
            return false;
        }
	}
	
	def.getPuntos = function(){
        this.puntos = 0;
        for(var i in this.apuestas){
            var apuesta = this.apuestas[i];
            this.puntos += apuesta.getPuntos();
        }
		return this.puntos;
	}

Class.Apuesta = 

	function (torneo, datos){
		this.torneo = torneo;
		this.id = datos.id;
		this.golesLocal = datos.gl;
		this.golesVisitante = datos.gv;
		this.resultado = this.getResultado();
		this.partido = '';
		this.puntos = '';
		
	}; def = Apuesta.prototype;
	
	def.getPartido = function(){
		
		if(this.partido == ''){
			this.partido = this.torneo.getPartido(this.id);
		}
		return this.partido;
	}
	
	def.getResultado = function(){
		return (this.golesLocal > this.golesVisitante)? 'L' : ((this.golesLocal < this.golesVisitante)? 'V' : 'E');
	}
	
	def.getPuntos = function(){
        this.puntos = 0;
        this.puntos += (this.resultado == this.getPartido().resultado)? 1 : 0;
        this.puntos += (this.golesLocal == this.getPartido().golesLocal && this.golesVisitante == this.getPartido().golesVisitante)? 2 : 0;
		return this.puntos;
	}