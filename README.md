# js-ts-migrate

JavascriptコードをTypescriptに変換する研究


clone

`git clone --recurse-submodules https://github.com/higolab/js-ts-migrate.git`


typescriptのインストール

```zsh
# install node by homebrew
brew install node
# install typescript
npm install -g typescript
```

クローンした後、tsファイルのみコピーする。

```zsh
cd tsrepos
rsync -av --include='*/' --include='*.ts' --exclude='*' ./ ../tsfiles
```

変換用jsonファイルもコピーする
```zsh
cp tsconfig.json ../tsfiles
```

空のフォルダを再帰的に削除する
```zsh
find . -type d -empty -delete
```

変換する
```zsh
cd ../tsfiles
# convert typescript to javascript
tsc
```
