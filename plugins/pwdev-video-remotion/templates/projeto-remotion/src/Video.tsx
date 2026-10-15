// Main composition of a pwdev-video-remotion project. Everything it shows comes from dados.json
// (the render plan): times are measured on the cut, positions are inside the platform safe zone.
// Only deterministic logic: no Date.now(), Math.random() or network calls.
import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {Audio} from '@remotion/media';
import {loadFont} from '@remotion/fonts';
import {CENAS} from './cenas.generated';
import dados from './dados.json';
import type {Bloco, Cue, Plano, Texto} from './tipos';

const plano = dados as unknown as Plano;

loadFont({family: 'Montserrat', url: staticFile('fonts/Montserrat.ttf'), weight: '100 900'});

const toFrames = (seconds: number, fps: number) => Math.round(seconds * fps);
const ZOOM_EASE = 0.35; // seconds to ease into a block's zoom

/** Camera zoom at time t: each block eases from the previous zoom to its own and holds it. */
export const zoomAt = (t: number, blocos: Bloco[]): {scale: number; origin: string} => {
  let scale = 1;
  let origin = '50% 35%';
  for (const b of [...blocos].sort((x, y) => x.inicio - y.inicio)) {
    if (t < b.inicio) break;
    const progress = Math.min(1, (t - b.inicio) / ZOOM_EASE);
    scale = scale + (b.zoom - scale) * Easing.out(Easing.quad)(progress);
    origin = b.origem;
  }
  return {scale, origin};
};

const Fala: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scale, origin} = zoomAt(frame / fps, plano.blocos);
  return (
    <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: origin}}>
      <OffthreadVideo
        src={staticFile(plano.video.arquivo)}
        trimBefore={toFrames(plano.video.inicio_midia, fps)}
        style={{width: '100%', height: '100%', objectFit: 'cover'}}
      />
    </AbsoluteFill>
  );
};

const Legenda: React.FC<{cue: Cue}> = ({cue}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = cue.inicio + frame / fps; // absolute time, to compare with the word times
  const enter = interpolate(frame, [0, toFrames(0.12, fps)], [0, 1], {extrapolateRight: 'clamp'});
  const {legenda, estilo, unidade} = plano;
  const destaque = legenda.estilo === 'destaque';
  const caixa = legenda.estilo === 'caixa';
  return (
    <div
      style={{
        position: 'absolute',
        top: legenda.topo,
        left: legenda.esquerda,
        width: legenda.largura,
        textAlign: 'center',
        fontFamily: `"${estilo.fonte}", Montserrat, sans-serif`,
        fontSize: legenda.tamanho,
        fontWeight: destaque ? 800 : 700,
        lineHeight: 1.15,
        textTransform: destaque ? 'uppercase' : 'none',
        color: estilo.texto,
        opacity: enter,
        transform: `translateY(${(1 - enter) * 14 * unidade}px)`,
        textShadow: `0 ${3 * unidade}px ${10 * unidade}px rgba(0,0,0,.65), 0 0 ${2 * unidade}px #000`,
      }}
    >
      <span
        style={
          caixa
            ? {background: 'rgba(10,10,10,.82)', padding: `${10 * unidade}px ${18 * unidade}px`,
               borderRadius: 12 * unidade, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone'}
            : undefined
        }
      >
      {cue.palavras.map((p, i) => {
        const next = cue.palavras[i + 1]?.inicio ?? cue.inicio + cue.duracao;
        // the word being said sits on a highlight pill with dark text (readable on any footage)
        const on = destaque && t >= p.inicio && t < next;
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              padding: `0 ${8 * unidade}px`,
              borderRadius: 10 * unidade,
              background: on ? estilo.destaque : 'transparent',
              color: on ? estilo.fundo : estilo.texto,
              marginRight: 4 * unidade,
            }}
          >
            {p.texto}
          </span>
        );
      })}
      </span>
    </div>
  );
};

const TextoNaTela: React.FC<{texto: Texto}> = ({texto}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {estilo, zona_segura: zona, unidade} = plano;
  const pop = spring({frame, fps, durationInFrames: toFrames(0.28, fps), config: {damping: 12}});
  const rotulo = texto.tipo === 'rotulo';
  return (
    <div
      style={{
        position: 'absolute',
        top: texto.topo,
        left: zona.x,
        width: zona.largura,
        textAlign: 'center',
        fontFamily: `"${estilo.fonte}", Montserrat, sans-serif`,
        fontWeight: 800,
        fontSize: texto.tamanho,
        lineHeight: 1.1,
        color: estilo.texto,
        textTransform: rotulo ? 'none' : 'uppercase',
        opacity: pop,
        transform: `translateY(${(1 - pop) * 30 * unidade}px) scale(${0.94 + 0.06 * pop})`,
        textShadow: rotulo ? undefined : `0 ${4 * unidade}px ${18 * unidade}px rgba(0,0,0,.6)`,
      }}
    >
      {rotulo ? (
        <span
          style={{
            display: 'inline-block',
            background: estilo.destaque,
            color: estilo.fundo,
            padding: `${10 * unidade}px ${22 * unidade}px`,
            borderRadius: 14 * unidade,
          }}
        >
          {texto.texto}
        </span>
      ) : (
        texto.texto
      )}
    </div>
  );
};

export const Video: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();
  const trilha = plano.audio.trilha;
  return (
    <AbsoluteFill style={{background: plano.estilo.fundo, overflow: 'hidden'}}>
      <Fala />
      {plano.cenas.map((c, i) => {
        const Cena = CENAS[c.src];
        return (
          <Sequence key={`cena${i}`} name={`cena ${c.src}`} from={toFrames(c.inicio, fps)}
                    durationInFrames={Math.max(1, toFrames(c.duracao, fps))}>
            <Cena duracao={c.duracao} sobreAPessoa={c.sobre_a_pessoa} estilo={plano.estilo}
                  zonaSegura={plano.zona_segura} unidade={plano.unidade} />
          </Sequence>
        );
      })}
      {plano.textos.map((t, i) => (
        <Sequence key={`texto${i}`} name={`texto: ${t.texto}`} from={toFrames(t.inicio, fps)}
                  durationInFrames={Math.max(1, toFrames(t.duracao, fps))}>
          <TextoNaTela texto={t} />
        </Sequence>
      ))}
      {plano.cues.map((c, i) => (
        <Sequence key={`legenda${i}`} name="legenda" from={toFrames(c.inicio, fps)}
                  durationInFrames={Math.max(1, toFrames(c.duracao, fps))}>
          <Legenda cue={c} />
        </Sequence>
      ))}
      {trilha ? (
        <Audio
          name="trilha"
          src={staticFile(trilha.arquivo)}
          volume={(f) =>
            trilha.volume *
            interpolate(f, [0, toFrames(0.5, fps), durationInFrames - toFrames(1, fps), durationInFrames],
              [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
          }
        />
      ) : null}
      {plano.audio.efeitos.map((e, i) => (
        <Sequence key={`sfx${i}`} name={`efeito ${e.arquivo}`} from={toFrames(e.inicio, fps)}>
          <Audio src={staticFile(e.arquivo)} volume={e.volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
