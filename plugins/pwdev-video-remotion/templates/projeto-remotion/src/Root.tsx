import React from 'react';
import {Composition} from 'remotion';
import dados from './dados.json';
import type {Plano} from './tipos';
import {Video} from './Video';

// dados.json is written by build.py; edit projeto.json and run `build.py montar`, never this data.
const plano = dados as unknown as Plano;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Principal"
      component={Video}
      durationInFrames={Math.max(1, Math.round(plano.duracao * plano.fps))}
      fps={plano.fps}
      width={plano.largura}
      height={plano.altura}
    />
  );
};
