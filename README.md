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
npm install -g typescript
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

ts-migrateのインストール
```zsh
npm install -g ts-migrate
```

js出力をコピー
```zsh
cp -r js-out/* js-out2
```

ts-migrateの実行
```zsh
cd js-out2
tsc --init
ts-migrate-full .
```
