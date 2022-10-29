'use strict';
const path = require('path');
const deleteitemsRecursive = require('./clean.js');

const pathArgs = [
	path.join(__dirname, '..', 'dbmanager', 'build'),
	path.join(__dirname, '..', 'build'),
];

console.log('Cleaning folders and files before build...');

pathArgs.forEach((pathToDelete) => deleteitemsRecursive(pathToDelete));

console.log('Successfully cleaned!');
