// Example custom scene: a number that counts up when the speaker says it.
// Copy, rename and adapt; reference it in projeto.json as "compositions/<file>.tsx".
// Time inside a scene starts at 0 at the scene's "inicio" (seconds on the cut).
import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CenaProps} from '../src/tipos';

// What this scene shows must come from the speech or the person's files: never invent numbers.
const VALOR = 3;
const ROTULO = 'dicas';
const ENTRADA = 0.1; // seconds after the scene start = when the word is said

const ExemploContador: React.FC<CenaProps> = ({duracao, estilo, zonaSegura, unidade}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const start = Math.round(ENTRADA * fps);
  const pop = spring({frame: frame - start, fps, config: {damping: 14}});
  const count = Math.round(interpolate(frame, [start, start + Math.round(0.6 * fps)], [0, VALOR], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));
  const exit = interpolate(frame, [Math.round((duracao - 0.25) * fps), Math.round(duracao * fps)], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        position: 'absolute',
        top: zonaSegura.y + 40 * unidade,
        left: zonaSegura.x,
        width: zonaSegura.largura,
        textAlign: 'center',
        fontFamily: `"${estilo.fonte}", Montserrat, sans-serif`,
        color: estilo.texto,
        opacity: pop * exit,
        transform: `scale(${0.8 + 0.2 * pop})`,
        textShadow: `0 ${4 * unidade}px ${18 * unidade}px rgba(0,0,0,.6)`,
      }}
    >
      <div style={{fontSize: 220 * unidade, fontWeight: 900, lineHeight: 1, color: estilo.destaque}}>{count}</div>
      <div style={{fontSize: 64 * unidade, fontWeight: 800, textTransform: 'uppercase'}}>{ROTULO}</div>
    </div>
  );
};

export default ExemploContador;
