import * as ts from "typescript";
import * as fs from "fs";
import * as path from "path";

// 引数でフォルダを受け取る
const inputDir = process.argv[2];
if (!inputDir) {
	console.error("Usage: ts-node analyze-types.ts <folder>");
	process.exit(1);
}
const absInputDir = path.resolve(inputDir);

// 指定フォルダ配下の .ts ファイルを再帰的に収集
function collectTSFiles(dir: string): string[] {
	let results: string[] = [];
	const entries = fs.readdirSync(dir, { withFileTypes: true });

	for (const entry of entries) {
		const fullPath = path.join(dir, entry.name);
		if (entry.isDirectory()) {
			results = results.concat(collectTSFiles(fullPath));
		} else if (entry.isFile() && fullPath.endsWith(".ts") && !fullPath.endsWith(".d.ts")) {
			results.push(fullPath);
		}
	}

	return results;
}

const fileNames = collectTSFiles(absInputDir);
if (fileNames.length === 0) {
	console.log("No .ts files found in", inputDir);
	process.exit(0);
}

const program = ts.createProgram(fileNames, {
	target: ts.ScriptTarget.ESNext,
	module: ts.ModuleKind.CommonJS,
});
const checker = program.getTypeChecker();

type ResultEntry = {
	path: string; // 相対パス
	name: string;
	type: string;
	line: number;
	file: string; // 相対パス
};

const results: ResultEntry[] = [];

for (const sourceFile of program.getSourceFiles()) {
	const absPath = path.resolve(sourceFile.fileName);
	if (!sourceFile.isDeclarationFile && absPath.startsWith(absInputDir)) {
		ts.forEachChild(sourceFile, visit(sourceFile));
	}
}

function visit(sourceFile: ts.SourceFile) {
	return function (node: ts.Node) {
		if (ts.isVariableStatement(node)) {
			for (const decl of node.declarationList.declarations) {
				if (ts.isIdentifier(decl.name)) {
					const symbol = checker.getSymbolAtLocation(decl.name);
					if (symbol) {
						const type = checker.getTypeOfSymbolAtLocation(symbol, decl);
						const typeStr = checker.typeToString(type);
						const { line } = ts.getLineAndCharacterOfPosition(sourceFile, decl.getStart());
						results.push({
							path: inputDir + '/',
							name: decl.name.text,
							type: typeStr,
							line: line + 1,
							file: path.relative(absInputDir, sourceFile.fileName),
						});
					}
				}
			}
		}
		ts.forEachChild(node, visit(sourceFile));
	};
}

// JSONとして標準出力
console.log(JSON.stringify(results, null, 2));
