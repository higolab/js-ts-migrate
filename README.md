# js-ts-migrate

JavascriptコードをTypescriptに変換する研究


この研究は中止することに決めました。

理由:

* LLMを使うとある程度正確にTypeScriptに変換でき、この研究の優位性を見出すのが難しいため。
* JavaScriptの仕様から、100%正確に型を推定することが難しいため。


### 準備

clone

`git clone --recurse-submodules https://github.com/higolab/js-ts-migrate.git`

typescriptのインストール

```zsh
# install node by homebrew
brew install node
# install typescript
npm install typescript
```

コマンドラインで変換する

`example`フォルダを対象にする場合は、以下のようにコマンドを実行します。

```zsh
FOLDER=example
# ts->js
npx tsc tsrepos/$FOLDER/**/*.ts -outDir ts-js/$FOLDER --target es2024 --module ES2022 --moduleResolution node --lib es2024 --types node > ts-js.$FOLDER.log 2>&1
#copy and js->ts
cp -r ts-js/$FOLDER ts-js-ts
npx ts-migrate-full --no-git ts-js-ts/$FOLDER > ts-js-ts.$FOLDER.log 2>&1
# extract types
npx tsx type-deduction/analyze-types.ts tsrepos/$FOLDER > type-deduction/original.$FOLDER.json
npx tsx type-deduction/analyze-types.ts ts-js-ts/$FOLDER > type-deduction/transpiled.$FOLDER.json
# compare types
python3 type-deduction/compare_types.py type-deduction/original.$FOLDER.json type-deduction/transpiled.$FOLDER.json > type-deduction/compare.$FOLDER.json
python3 type-deduction/analyze_type_changes.py type-deduction/compare.$FOLDER.json > type-deduction/analyze.$FOLDER.json
```

一行にまとめて、
`FOLDER=example ; npx tsc tsrepos/$FOLDER/**/*.ts -outDir ts-js/$FOLDER --target es2024 --module ES2022 --moduleResolution node --lib es2024 --types node > ts-js.$FOLDER.log 2>&1 ; cp -r ts-js/$FOLDER ts-js-ts ; npx ts-migrate-full ts-js-ts/$FOLDER > ts-js-ts.$FOLDER.log 2>&1 ; npx tsx type-deduction/analyze-types.ts tsrepos/$FOLDER > type-deduction/original.$FOLDER.json ; npx tsx type-deduction/analyze-types.ts ts-js-ts/$FOLDER > type-deduction/transpiled.$FOLDER.json ; python3 type-deduction/compare_types.py type-deduction/original.$FOLDER.json type-deduction/transpiled.$FOLDER.json > type-deduction/compare.$FOLDER.json python3 type-deduction/analyze_type_changes.py type-deduction/compare.$FOLDER.json > type-deduction/analyze.$FOLDER.json`
