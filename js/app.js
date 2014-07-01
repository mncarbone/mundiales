Class = window;

Class.Torneo = 

	function(participantes, partidos){
		this.nombre = 'Brasil 2014';
		this.partidos = {};
		this.participantes = {};
		this.cargarParticipantes(participantes);
		this.cargarPartidos(partidos);
	}; def = Torneo.prototype;

	def.cargarParticipantes = function(participantes){
		var tot = participantes.length;
		for(var i=0; i < tot; i++){
			datos = participantes[i];
			var p = new Participante(this, datos)
			this.participantes[datos.id] = p;
		}
	}

	def.cargarPartidos = function(partidos){
		var tot = partidos.length;
		for(var i=0; i < tot; i++){
			datos = partidos[i];
			var p = new Partido(this, datos);
			this.partidos[p.id] = p;
		}
	}
	
	def.apuestasPara = function(unPartido){
		var apuestas = [];
		for(idParticipante in this.participantes){
			var participante = this.participantes[idParticipante];
			apuestas.push(participante.apuestaPara(unPartido));
		}
		return apuestas;
	}

	
	def.getPartido = function(id){
		return this.partidos[id];
	}
	
	def.getPartidos = function(){
		return this.partidos;
	}


Class.Equipo = 

	function(codigo){
		this.codigo = codigo;
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
		this.golesLocal = datos.home_team.goals;
		this.golesVisitante = datos.away_team.goals;
		this.resultado = this.getResultado();
		this.apuestasPor = {
			'L':this.cantApuestasPor('L'),
			'E':this.cantApuestasPor('E'),
			'V':this.cantApuestasPor('V')
		};
	}; def = Partido.prototype;
	
	def.cantApuestasPor = function(resultado){
		var apuestas = this.torneo.apuestasPara(this);
		var tot = apuestas.length;
		var totApuestasPor=0;
		for(var i=0; i<tot; i++){
			if(apuestas[0].resultado == resultado){
				totApuestasPor++;
			}
		}
		return totApuestasPor;
	}
	
	def.getResultado = function(){
		return (this.golesLocal > this.golesVisitante)? 'L' : ((this.golesLocal < this.golesVisitante)? 'V' : 'E');
	}

	
Class.Participante = 

	function (torneo, datos){
		this.torneo = torneo;
		this.id = datos.id;
		this.nombre = datos.nombre;
		this.apuestas = {};
		this.cargarApuestas(datos.apuestas);
		this.puntos = this.getPuntos();
	}; def = Participante.prototype;
	
	def.cargarApuestas = function(apuestas){
		var tot = apuestas.length;
		for(var i=0; i<tot; i++){
			var datos = apuestas[i];
			var a = new Apuesta(this.torneo, datos);
			this.apuestas[datos.id] = a;
		}
	}
	
	def.apuestaPara = function(unPartido){
		return this.apuestas[unPartido.id];
	}
	
	def.getPuntos = function(){
		var tot = 0;
		for(idApuesta in this.apuestas){
			var apuesta = this.apuestas[idApuesta];
			tot += apuesta.puntos
		}
		return tot;
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
		if(this.puntos == ''){
			this.puntos = 0;
			this.puntos += (this.resultado == this.getPartido().resultado)? 1 : 0;
			this.puntos += (this.golesLocal == this.getPartido().golesLocal && this.golesVisitante == this.getPartido().golesVisitante)? 2 : 0;
			
		}
		return this.puntos
	}
	