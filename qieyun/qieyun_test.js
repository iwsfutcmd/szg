import Qieyun, { 音韻地位 } from "qieyun";
import { putonghua, gwongzau, baxter } from "qieyun-examples";
import fs from "fs";
const 楊 = Qieyun.query字頭("楊")[0].音韻地位;

const 三字經 = fs
  .readFileSync("三字經.txt", "utf8")
  .replace(/\n/g, "")
  .split("");
const san1zi2jing1 = fs
  .readFileSync("san1zi2jing1.txt", "utf8")
  .replace(/\n/g, " ")
  .split(" ");
const saam1zi6ging1 = fs
  .readFileSync("saam1zi6ging1.txt", "utf8")
  .replace(/\n/g, " ")
  .split(" ");
const lzh_cmn_yue = 三字經.map((字, i) => [
  字,
  san1zi2jing1[i],
  saam1zi6ging1[i],
  Qieyun.query字頭(字).map((e) => e.音韻地位),
]);

const fixed_putonghua = 音韻地位 => {
  const s = putonghua(音韻地位);
  const output = [];
  if (!s.match(/^[a-z]+[1-4]$/)) {
    ["1", "2", "3", "4"].forEach((n) => output.push(s + n));
  } else {
    output.push(s);
  }
  return output;
}

const output = 三字經.map((字, i) => {
  const possible_lzh = Qieyun.query字頭(字).map((e) => e.音韻地位).filter(e => fixed_putonghua(e).includes(san1zi2jing1[i]));
  return [
    字,
    san1zi2jing1[i],
    saam1zi6ging1[i],
    possible_lzh.map(gwongzau)
  ];
});

console.log(output.filter(e => !e[3].includes(e[2])));

const fails = lzh_cmn_yue.filter((e) => {
  const cmn = e[1];
  const gcmn = e[3].map(putonghua);
  const generated_cmn = [];
  gcmn.forEach((s) => {
    if (!s.match(/^[a-z]+[1-4]$/)) {
      ["1", "2", "3", "4"].forEach((n) => generated_cmn.push(s + n));
    } else {
      generated_cmn.push(s);
    }
  });
  // e[2].forEach(音韻地位 => {
  //   if (音韻地位.聲 === '入') {
  //     ["1", "2", "3", "4"].forEach(n => generated_cmn.push(putonghua(音韻地位) + n));
  //   } else {
  //     generated_cmn.push(putonghua(音韻地位));
  //   }
  // })
  // return generated_cmn;
  return !generated_cmn.includes(cmn);
});

const qiter = Qieyun.iter音韻地位();

// console.log(fails.map((e) => [e[0], e[1], e[2], e[3].map(putonghua)]));
const no_cmn = Array.from(qiter, (i) =>
  putonghua(i) === "?" ? [i.代表字, i.描述] : null
).filter((i) => i);

// for (const i of qiter) {
//   const cmn = putonghua(i);
//   if (cmn === "?") {
//     console.log(i.代表字);
//     console.log(i);
//   }
// }
// console.log(no_cmn);
// console.log(no_cmn.length);
// console.log(Qieyun.query字頭("地")[0].音韻地位.編碼);
