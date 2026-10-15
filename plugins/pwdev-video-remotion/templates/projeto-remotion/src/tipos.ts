// Types of src/dados.json: the render plan (pwdev-plano-render/1) produced by
// `pwdev-media video plano-render` and rewritten by build.py with paths under public/.
import type React from 'react';

export type Estilo = {fonte: string; texto: string; destaque: string; fundo: string};

export type Palavra = {texto: string; inicio: number};

export type Cue = {inicio: number; duracao: number; palavras: Palavra[]};

export type Texto = {
  inicio: number;
  duracao: number;
  texto: string;
  tipo: 'rotulo' | 'titulo';
  posicao: 'topo' | 'centro' | 'base';
  topo: number;
  tamanho: number;
};

export type Bloco = {inicio: number; duracao: number; zoom: number; origem: string};

export type Cena = {inicio: number; duracao: number; src: string; sobre_a_pessoa: boolean};

export type Plano = {
  schema: 'pwdev-plano-render/1';
  nome: string;
  formato: string;
  largura: number;
  altura: number;
  fps: number;
  duracao: number;
  amostra: boolean;
  janela: {inicio: number; fim: number};
  video: {arquivo: string; inicio_midia: number};
  estilo: Estilo;
  legenda: {estilo: 'discreta' | 'destaque'; topo: number; esquerda: number; largura: number; tamanho: number};
  zona_segura: {x: number; y: number; largura: number; altura: number};
  unidade: number;
  cues: Cue[];
  textos: Texto[];
  blocos: Bloco[];
  cenas: Cena[];
  audio: {
    trilha: {arquivo: string; volume: number} | null;
    efeitos: {inicio: number; arquivo: string; volume: number}[];
  };
};

/** Props every custom scene in compositions/ receives. Time inside a scene starts at 0. */
export type CenaProps = {
  duracao: number;
  sobreAPessoa: boolean;
  estilo: Estilo;
  zonaSegura: Plano['zona_segura'];
  unidade: number;
};

export type CenaComponent = React.FC<CenaProps>;
