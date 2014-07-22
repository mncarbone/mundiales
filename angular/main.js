var brasil2014 = angular.module('brasil2014', []);

function mainController($scope, $http) {
    $scope.formData = {};

    // Cuando se cargue la página, pide del API todos los partidos
    $http.get('http://worldcup.sfg.io/matches?by_date=ASC')
        .success(function(data) {
            $scope.partidos = data;
            console.log('OK partidos');
        })
        .error(function(data) {
            console.log('Error: ' + data);
        });
		
    $http.get('http://jsonblob.com/api/jsonBlob/53ad7745e4b07a1c9f44e5a6')
        .success(function(data) {
            $scope.participantes = data;
            console.log('OK participantes');
        })
        .error(function(data) {
            console.log('Error: ' + data);
        });
		
    $scope.diaAnt = '';
    $scope.nuevo_dia = true;
    
    $scope.fecha = function(obj){
		var datetime = obj.datetime.split('T');
		var dia = datetime[0];
		var horamin = datetime[1].split('.')[0].split(':');
		var hora = horamin[0] + ':' + horamin[1];
        $scope.nuevo_dia = ($scope.diaAnt != dia);
        $scope.diaAnt = dia;
        return dia;
    }
    
    $scope.bandera = function(codigo){
            $scope.blank = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
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
			return codes[codigo];            
    }
/*
    // Cuando se añade un nuevo TODO, manda el texto a la API
    $scope.createTodo = function(){
        $http.post('/api/todos', $scope.formData)
            .success(function(data) {
                $scope.formData = {};
                $scope.todos = data;
                console.log(data);
            })
            .error(function(data) {
                console.log('Error:' + data);
            });
    };

    // Borra un TODO despues de checkearlo como acabado
    $scope.deleteTodo = function(id) {
        $http.delete('/api/todos/' + id)
            .success(function(data) {
                $scope.todos = data;
                console.log(data);
            })
            .error(function(data) {
                console.log('Error:' + data);
            });
    };
    */
}