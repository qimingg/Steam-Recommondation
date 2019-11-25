// controller.js
#!/usr/bin/env node

var oracledb = require('oracledb');
angular
  .module('app')
  .controller('dashboardCtrl1', dashboardCtrl1)

  dashboardCtrl1.$inject = ['$scope'];
         function dashboardCtrl1($scope) {
          $scope.data = 1;
          function sendQuery(queryString, callback){
              oracledb.getConnection({
                user: 'admin',
                password: 'CIS550project',
                connectString: '(DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)'+
                '(HOST = cis550project.cleeuzvzzpg3.us-east-1.rds.amazonaws.com)'+
                '(PORT = 1521))(CONNECT_DATA =(SID = SteamDB)))'
              }, function(err, connection) {
                if (err) {
                  console.error(err.message);
                  return;
                }
                console.log("\nQuery : "+queryString);
                connection.execute(queryString, [],{ maxRows: 1000 },
                function(err, result) {
                  if (err) {
                    console.error(err.message);
                    doRelease(connection);
                    return;
                  }
                  callback(result);
                  doRelease(connection);
                });
              });
            }

            function doRelease(connection) {
              connection.release(
                function(err) {
                  if (err) {
                  console.error(err.message);}
                }
              );
            }

          var query = `
            SELECT DISTINCT (FLOOR(year/10)*10) AS decade
            FROM (
              SELECT DISTINCT release_year as year
              FROM \"Movies\"
              ORDER BY release_year
            ) y
          `;
          
          $scope.data = 1;

          $scope.test = sendQuery(query, function(err, rows, fields) {
            if (err) console.log(err);
            else {
              console.log(rows);
              res.json(rows);
            }
          });
         }