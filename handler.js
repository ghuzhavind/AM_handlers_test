const token = 'YOUR_TOKEN_HERE';
const multicube = 'test';
let om;

/**
 * Create connection with model
 *
 * @param {String} token  -- Your personal token
 * @returns {Connection} -- Connection with model
 */
async function connect(token) {
	const params = {
		url: 'https://wsXXX.domain.com/',
		wsUrl: 'wss://wsXXX.domain.com/ws',
		token,
		modelId: 'MODEL_ID',
	};
	return await OM.connectAsync(
		params.url,
		params.wsUrl,
		params.token,
		params.modelId
	);
}

// ----------------- by number ----------------

// async function writeData(om, number) {
// const mcTab = om.multicubes.multicubesTab().open('test');

// const pivot = mcTab
// .pivot()
// .columnsFilter('test')
// .rowsFilter('#' + number);

// const grid = await pivot.createAsync();
// const generator = grid.range(0, -1, 0, -1).generator();
// const cb = om.common.createCellBuffer().canLoadCellsValues(false);

// for (const chunk of generator) {
// for (const cell of (await chunk.cellsAsync()).all()) {
// cb.set(cell, number);
// }
// }

// await cb.applyAsync();
// await om.close();
// return { number };
// }

// ----------------- brute-force ----------------

/**
 * Write received number into first empty row in multicube
 *
 * @param {OM} om -- om connection
 * @param {Number} number -- request number
 * @returns
 */
async function writeData(om, number) {
	const mcTab = om.multicubes.multicubesTab().open('test');
	const pivot = mcTab.pivot().columnsFilter('test2');
	const grid = await pivot.createAsync();
	const generator = grid.range(0, -1, 0, -1).generator();
	const cb = om.common.createCellBuffer().canLoadCellsValues(false);

	for (const chunk of generator) {
		const rowLabels = await chunk.rowsAsync();

		for (const rowLabelsGroup of await rowLabels.allAsync()) {
			const rowLabel = rowLabelsGroup.first().label();

			for (const cell of rowLabelsGroup.cells().all()) {
				const cellValue = cell.getValue();

				if (cellValue === '') {
					cb.set(cell, rowLabel);
					await cb.applyAsync();
					await om.close();
					return { rowLabel };
				}
			}
		}
	}
	await cb.applyAsync();
	await om.close();
	return { number };
}

/**
 * Call the received function with received arguments and return result or error
 *
 * @param {Function} callback
 * @param  {object} args
 * @returns {object} request result -- written row label or error and elapsed time
 */
async function measure(callback, ...args) {
	const start = process.hrtime();
	let result = undefined;
	let error = undefined;

	try {
		result = await callback(...args);
	} catch (err) {
		error = err.message ? err.message : String(err);
	}

	const elapsed = process.hrtime(start);
	const elapsedMs = elapsed[1] / 1000000; // nsec to msec
	const time = `${elapsed[0]}s, ${elapsedMs.toFixed(3)}ms`;

	return { result, error, time };
}

/**
 * Web-handler for keeping alive connection
 */
OM.web('keepalive', async request => {
	await sleep(parseInt(request.body.sleep) || 10000);
	return `Keeper done!`;
});

/**
 * Web-handler for testing
 */
OM.web('test', async request => {
	if (!om) {
		om = await connect(request.body.token || token);
	}

	let body;

	try {
		body = JSON.parse(request.body);
	} catch {
		body = request.body;
	}

	const grid = await measure(writeData, om, body.number);
	return JSON.stringify(grid);
});
