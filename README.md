# js-ts-migrate

JavascriptコードをTypescriptに変換する研究

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

### 動作確認

動作確認の為にtranspile_testフォルダを使用

```zsh
cd transpile_test

# 1st way (creating tsconfig.json)
tsc --init
tsc

# 2nd way (running tsc without tsconfig.json)
tsc main.ts

```

今回は1st wayを使用する

### 変換

クローンした後、tsファイルのみコピーする。.d.tsファイルは除外する。

```zsh
cd tsrepos
rsync -av --include='*/' --exclude='*.d.ts' --include='*.ts' --exclude='*' ./ ../tsfiles > /dev/null
```

変換用jsonファイルもコピーする

```zsh
cp tsconfig.json ../tsfiles
```

空のフォルダを再帰的に削除する

```zsh
find ../tsfiles -type d -empty -delete
```

変換する

```zsh
cd ../tsfiles
# convert typescript to javascript
tsc
```

ドットで始まるフォルダも対象に含めるなら、

```json
{
  "include": [
    "**/.*/**/*.ts"  // ドットで始まる全てのフォルダ内の TypeScript ファイルを対象に追加
  ],
}
```

を追記する

ファイルが1:1になっているか確認する

```zsh
cd ..
ls -R1 tsfiles >tsfiles.txt
ls -R1 js-out >js-out.txt
# 余計な文字列を削除
sed -i '' 's/tsfiles//g' tsfiles.txt 
sed -i '' 's/\.ts//g' tsfiles.txt
sed -i '' 's/js-out//g' js-out.txt 
sed -i '' 's/\.js//g' js-out.txt
```

vueのみ対象にする
ファイル数が合わない原因
変換できていないファイル
.d.tsファイル(tsでのみ使用する、型情報が定義されているファイル)

js出力をコピー

```zsh
cp -r js-out/* js-out2
```

ts-migrateの実行

```zsh
cd js-out2
tsc --init
npm install --save-dev ts-migrate
npx ts-migrate-full vue
```

型情報を取り出す

```zsh
cd type-export
npm init -y
npm install typescript
cp -r ../js-out2 transpiled
rm -rf transpiled/node_modules
node extract-types.ts transpiled > transpiled.txt
cp -r ../tsfiles original
node extract-types.ts original > original.txt
```

コマンドラインで変換する

```zsh
#install packages
npm i undici-types url stream estree-walker magic-string lru-cache typescript vue
npm i --save-dev @types/node @vue/compiler-sfc @babel/types @babel/parser @compiler/codeframe
#ts->js
npx tsc tsrepos/example/**/*.ts -outDir ts-js/transpiled/example --target es2024 --module ES2022 --moduleResolution node --lib es2024 --types node
#copy and js->ts
cp -r ts-js/transpiled ts-js-ts
npx ts-migrate-full ts-js-ts/transpiled
# extract types
npx tsx type-deduction/analyze-types.ts tsrepos/example > type-deduction/original.txt
npx tsx type-deduction/analyze-types.ts ts-js-ts/transpiled/example > type-deduction/transpiled.txt
```

`example`フォルダを対象にする場合は、以下のようにコマンドを実行します。
```zsh
npx tsc tsrepos/example/**/*.ts -outDir ts-js/example --target es2024 --module ES2022 --moduleResolution node --lib es2024 --types node
#copy and js->ts
cp -r ts-js/example ts-js-ts
npx ts-migrate-full ts-js-ts/example
# extract types
npx tsx type-deduction/analyze-types.ts tsrepos/example > type-deduction/original.txt
npx tsx type-deduction/analyze-types.ts ts-js-ts/example > type-deduction/transpiled.txt
```



```zsh
#module
FOLDER=example
npx tsc tsrepos/$FOLDER/**/*.ts -outDir ts-js/$FOLDER --target es2024 --module ES2022 --moduleResolution node --lib es2024 --types node > ts-js.$FOLDER.log
#copy and js->ts
cp -r ts-js/$FOLDER ts-js-ts
npx ts-migrate-full ts-js-ts/$FOLDER > ts-js-ts.$FOLDER.log
# extract types
npx tsx type-deduction/analyze-types.ts tsrepos/$FOLDER > type-deduction/original.$FOLDER.json
npx tsx type-deduction/analyze-types.ts ts-js-ts/$FOLDER > type-deduction/transpiled.$FOLDER.json
```

vueの場合
```zsh
npm install magic-string postcss @vue/consolidate hash-sum postcss-selector-parser merge-source-map he
cd tsrepos/vue
npx tsc

```