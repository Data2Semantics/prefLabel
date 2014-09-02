'use strict';

var prefLabelApp = angular.module('prefLabelApp', ['ui.bootstrap']);

prefLabelApp.controller('FormCtrl', ['$scope', '$http', function ($scope, $http) {
  $scope.lastResponse = {};
  $scope.acceptHeader = "application/json";
  $scope.exampleURI = "http://www.wikidata.org/entity/P103";
  $scope.encodedURI = function() {
    if ($scope.textURI) {
      return encodeURIComponent($scope.textURI);
    }
  };
  $scope.getLabel = function() {
    if (!$scope.textURI) {
      $scope.textURI = $scope.exampleURI;
    };
    $http.get('./api/v1/label/' + $scope.encodedURI(),
      {'headers': {'Accept': $scope.acceptHeader}}).
    success(function (data, status, headers, config, statusText) {
      $scope.lastResponse = {
        "status": status,
        "ok": (status == 200),
        "headers": headers(),
        "data": data
      };
    }).
    error(function (data, status, headers, config, statusText) {
      $scope.lastResponse = {
        "status": status,
        "ok": false,
        "headers": headers(),
        "data": data,
      };
    });
  };
}]);
