from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.database import engine
from app.models import Laboratorio, Usuario, Equipamento, FichaTecnica, Experimento, Reserva, Manutencao

def povoar():
    with Session(engine) as session:
        if session.exec(select(Laboratorio)).first() is not None:
            print("Banco ja possui laboratorios. Povoamento nao executado.")
            return
        laboratorio = Laboratorio(nome="Laboratorio de Informatica", localizacao="Bloco 1 - Sala 101", ativo=True)
        usuario = Usuario(nome="Maria Silva", email="maria@universidade.edu", ativo=True)
        session.add_all([laboratorio, usuario])
        session.commit()
        session.refresh(laboratorio)
        session.refresh(usuario)
        equipamentos = [
            Equipamento(nome=f"Computador {n:02d}", patrimonio=f"LAB-{n:03d}",
                        laboratorio_id=laboratorio.id, status="disponivel", ativo=True)
            for n in range(1, 11)
        ]
        session.add_all(equipamentos)
        session.commit()
        for equipamento in equipamentos:
            session.refresh(equipamento)
        ficha = FichaTecnica(equipamento_id=equipamentos[0].id, fabricante="Dell", modelo="Optiplex")
        experimento = Experimento(nome="Aula pratica", laboratorio_id=laboratorio.id,
                                  responsavel_id=usuario.id, descricao="Teste de equipamentos")
        experimento.equipamentos = equipamentos[:2]
        session.add_all([ficha, experimento])
        session.commit()
        session.refresh(experimento)
        inicio = datetime.now().replace(microsecond=0) + timedelta(days=2)
        reserva = Reserva(equipamento_id=equipamentos[0].id, usuario_id=usuario.id,
                          experimento_id=experimento.id, inicio=inicio,
                          fim=inicio + timedelta(hours=2), status="ativa")
        manutencao = Manutencao(equipamento_id=equipamentos[2].id,
                                descricao="Verificacao preventiva",
                                inicio=inicio, fim=inicio + timedelta(hours=3),
                                status="aberta", observacoes="Manutencao programada")
        session.add_all([reserva, manutencao])
        session.commit()
        print("Povoamento concluido: 10 equipamentos e registros relacionados.")

if __name__ == "__main__":
    povoar()
